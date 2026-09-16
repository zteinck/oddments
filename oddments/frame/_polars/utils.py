from functools import wraps

import polars as pl
import polars.selectors as cs

from ...validation import (
    Validator,
    sanitize_subset,
    )

_DEFAULT_SAMPLE_SIZE = 5


def _preserve_input_type(func):
    '''
    Description
    ------------
    Decorator that accepts a Polars object of variable type, converts it to
    a LazyFrame for processing, and recasts the return value to preserve the
    original input type.

    Parameters
    ------------
    obj : pl.LazyFrame | pl.DataFrame | pl.Series
        Polars object.
    subset : None | array-like
        Subset of column names the decorated function should consider.
        If None, all columns are considered.
    nan_to_null : bool
        If True, NaN values are replaced with None in the query plan before
        being passed to the decorated function.
    name : None | str
        Optional name used to identify 'obj' in error messages.
    kwargs : dict
        Keyword arguments passed to the decorated function.

    Returns
    ------------
    result : None | pl.LazyFrame | pl.DataFrame | pl.Series
        Decorated function's return value recast to match the original input
        type.
    '''

    @wraps(func)
    def wrapper(
        obj,
        subset=None,
        nan_to_null=False,
        name=None,
        **kwargs
        ):

        # validate input type
        (
        Validator(
            types=(
                pl.LazyFrame,
                pl.DataFrame,
                pl.Series,
                )
            )
        .validate(
            obj=obj
            )
        )

        # capture input's original type
        input_type = type(obj)

        # create a copy of the input
        obj = obj.clone()

        # check if the input is a LazyFrame
        not_lazy = not isinstance(obj, pl.LazyFrame)

        # return early if non-lazy input is empty
        if not_lazy and obj.is_empty():
            return obj

        # check if input is a Series
        is_series = not_lazy and isinstance(obj, pl.Series)

        # cast Series to DataFrame, if necessary
        if is_series:
            obj = obj.to_frame()

        # get list of column names
        superset = list(
            obj.columns
            if not_lazy
            else obj.collect_schema().names()
            )

        # sanitize subset
        subset = sanitize_subset(subset, superset)

        # cast input to LazyFrame, if necessary
        lf = obj.lazy() if not_lazy else obj

        # replace NaN with None
        if nan_to_null:
            lf = lf.fill_nan(None)

        # name housekeeping
        (
        Validator(
            types=str,
            allow_none=True,
            allow_blank=False,
            )
        .validate(
            name=name
            )
        )

        if name is None:
            name = input_type.__name__
        elif len(name.split()) == 1:
            name = repr(name)

        # call decorated function
        result = func(
            lf=lf,
            subset=subset,
            name=name,
            **kwargs
            )

        # verify decorated function returned a LazyFrame
        (
        Validator(
            types=pl.LazyFrame,
            allow_none=True,
            )
        .validate(
            result=result
            )
        )

        # return early if result is None
        if result is None:
            return

        # if input was not a LazyFrame, materialize the DataFrame
        if not_lazy:
            result = result.collect()

        # recast return value to Series, if necessary
        if is_series:
            if result.width == 1:
                result = result.to_series()
            else:
                raise ValueError(
                    'Expected a single-column DataFrame, got '
                    f'{result.width:,} columns.'
                    )

        # verify return value mirrors the original input type
        Validator(types=input_type).validate(result=result)

        return result

    return wrapper


@_preserve_input_type
def assert_no_nulls(lf, subset, name, how='any'):
    '''
    Description
    ------------
    Raises an error when subset column(s) contain nulls, based on the
    selected criterion.

    Parameters
    ------------
    how : str
        Determines how a row qualifies as invalid:
            • 'any' → Rows that contain at least one null value in any subset
                column.
            • 'all' → Rows entirely comprised of null values in the subset
                column(s).

    Returns
    ------------
    None
    '''

    how_map = {
        'any': pl.any_horizontal,
        'all': pl.all_horizontal,
        }

    (
    Validator(
        types=str,
        whitelist=list(how_map.keys()),
        )
    .validate(
        how=how
        )
    )

    # select invalid rows based on the selected criterion
    lf = lf.filter(
        how_map[how](
            pl.col(subset).is_null()
            )
        )

    # get total number of invalid rows
    n_rows = lf.select(pl.len()).collect().item()

    # return early if no invalid rows were identified
    if n_rows == 0:
        return

    # get a sample of invalid rows for reference
    df = lf.limit(_DEFAULT_SAMPLE_SIZE).collect()

    raise ValueError(
        f'Nulls detected in {name}. Showing {df.height:,} of {n_rows:,} '
        f'rows with {how} nulls in subset {subset}:\n\n{df}'
        )


@_preserve_input_type
def _assert_unique_with_polars(
    lf,
    subset,
    name,
    null_policy='error',
    ):
    '''
    Description
    ------------
    Raises an error if duplicate rows are detected.

    Parameters
    ------------
    null_policy : str
        Policy controlling how null values are handled:
            • 'include' → Include rows containing nulls in duplicate
                detection (i.e. null == null).
            • 'exclude' → Exclude rows containing nulls from duplicate
                detection (i.e. null != null).
            • 'error' → Raise an error if any null values are present in
                subset columns.

    Returns
    ------------
    None
    '''

    freq = 'len'

    if freq in set(subset):
        raise ValueError(
            f'Column name {freq!r} is reserved for the frequency column '
            'created by this operation.'
            )

    (
    Validator(
        types=str,
        whitelist=['include','exclude','error'],
        )
    .validate(
        null_policy=null_policy
        )
    )

    if null_policy == 'exclude':
        lf = lf.filter(
            pl.all_horizontal(
                pl.col(subset).is_not_null()
                )
            )

    elif null_policy == 'error':
        assert_no_nulls(
            lf,
            subset=subset,
            name=name,
            how='any',
            )

    dupe_counts = (
        lf
        .group_by(subset)
        .len()
        .filter(pl.col(freq) > 1)
        .top_k(_DEFAULT_SAMPLE_SIZE, by=freq)
        .select([*subset, freq])
        .collect()
        )

    if not dupe_counts.is_empty():
        raise ValueError(
            f'Duplicates detected in {name}:\n\n{dupe_counts}'
            )


@_preserve_input_type
def _trim_nulls_with_polars(
    lf,
    subset,
    name,
    which='both',
    how='any',
    allow_nulls=False,
    ):
    '''
    Description
    ------------
    Drops leading and/or trailing rows that contain null values in the subset
    columns.

    Parameters
    ------------
    which : str
        Specifies which rows to drop based on the presence of null values.
            • 'both' → Drop both leading and trailing rows.
            • 'leading' → Drop only leading rows.
            • 'trailing' → Drop only trailing rows.
    how : str
        Determines what qualifies a row to be dropped.
            • 'any' → Rows that contain at least one null value in any subset
                column are dropped.
            • 'all' → Rows entirely comprised of null values in the subset
                column(s) are dropped.
    allow_nulls : bool
        If False, an error is raised if any null values remain.

    Returns
    ------------
    lf : pl.LazyFrame
        Amended logical plan.
    '''

    # Note: the mapping is intentionally inverted becaues the check is for not
    # null.
    how_map = {
        'any': pl.all_horizontal,
        'all': pl.any_horizontal,
        }

    (
    Validator(
        types=str,
        whitelist=list(how_map.keys()),
        )
    .validate(
        how=how
        )
    )

    mask = how_map[how](pl.col(subset).is_not_null())

    not_leading = mask.cum_sum() > 0
    not_trailing = mask.reverse().cum_sum().reverse() > 0

    which_map = {
        'leading': not_leading,
        'trailing': not_trailing,
        'both': not_leading & not_trailing,
        }

    (
    Validator(
        types=str,
        whitelist=list(which_map.keys()),
        )
    .validate(
        which=which
        )
    )

    lf = lf.filter(which_map[which])

    if not allow_nulls:
        assert_no_nulls(
            lf,
            subset=subset,
            name=name,
            how='any',
            )

    return lf


@_preserve_input_type
def _purge_whitespace_with_polars(lf, subset, name):
    '''
    Description
    ------------
    Strips leading and trailing whitespace from subset names and values.
    Subset values that only contain whitespace are replaced with null.

    Parameters
    ------------
    ...

    Returns
    ------------
    lf : pl.LazyFrame
        Amended logical plan.
    '''

    mapping = {
        col: col.strip()
        for col in subset
        }

    new_subset = list(mapping.values())

    lf = (
        lf
        .rename(
            mapping=mapping,
            strict=True,
            )
        .with_columns(
            (cs.by_name(new_subset) & cs.string())
            .str.strip_chars().replace('', None)
            )
        .fill_nan(None)
        )

    return lf