import polars as pl
import polars.selectors as cs
from functools import wraps

from ...validation import validate_value


def sanitize_subset(
    subset,
    superset=None,
    subset_name='subset',
    superset_name='superset'
    ):
    '''
    Description
    ------------
    Sanitizes a subset of column names by ensuring it is a list of unique
    strings and optionally validates membership against a superset.

    Parameters
    ------------
    subset : None | str | array-like[str]
        Subset of column names. If None, the superset is returned.
    superset : None | str | array-like[str]
        Superset of column names.
    subset_name : str
        Subset name used in error messages.
    superset_name : str
        Superset name used in error messages.

    Returns
    ------------
    subset : list
        Sanitized subset of column names.
    '''

    def sanitize(value, name):

        validate_value(
            value=value,
            name=name,
            types=(str, list, tuple, set),
            none_ok=True,
            )

        if value is None:
            return None

        if isinstance(value, str):
            return [value]

        s = pl.Series(
            name=name,
            values=value,
            dtype=str,
            strict=True,
            nan_to_null=True,
            )

        out = (
            s
            .drop_nulls()
            .unique(maintain_order=True)
            .to_list()
            )

        validate_value(
            value=out,
            name=f'sanitized {name!r}',
            types=list,
            empty_ok=False,
            )

        return out


    subset = sanitize(subset, subset_name)
    superset = sanitize(superset, superset_name)

    if subset is None:
        return superset

    if superset is None:
        return subset

    whitelist = set(superset)

    extra_cols = [
        col for col in subset
        if col not in whitelist
        ]

    if extra_cols:
        raise ValueError(
            f'{subset_name} includes column names not '
            f'found in {superset_name}: {extra_cols}'
            )

    return subset


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
    out : None | pl.LazyFrame | pl.DataFrame | pl.Series
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
        validate_value(
            value=obj,
            name='obj',
            types=(
                pl.LazyFrame,
                pl.DataFrame,
                pl.Series,
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
        validate_value(
            value=name,
            name='name',
            types=str,
            none_ok=True,
            empty_ok=False,
            )

        if name is None:
            name = input_type.__name__

        # call decorated function
        out = func(
            lf=lf,
            subset=subset,
            name=name,
            **kwargs
            )

        # verify decorated function returned a LazyFrame
        validate_value(
            value=out,
            name='out',
            types=pl.LazyFrame,
            none_ok=True,
            )

        # return early if result is None
        if out is None:
            return

        # if input was not a LazyFrame, materialize the DataFrame
        if not_lazy:
            out = out.collect()

        # recast return value to Series, if necessary
        if is_series:
            if out.width == 1:
                out = out.to_series()
            else:
                raise ValueError(
                    'Expected a single-column DataFrame, '
                    f'got {out.width:,} columns.'
                    )

        # verify return value mirrors the original input type
        validate_value(
            value=out,
            name='output',
            types=input_type,
            )

        return out

    return wrapper


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
            f'Column name {freq!r} is reserved for the '
            'frequency column created by this operation.'
            )

    validate_value(
        value=null_policy,
        name='null_policy',
        types=str,
        whitelist=['include','exclude','error']
        )

    if null_policy == 'error':
        null_counts = (
            lf.select([
                pl.col(col).null_count().alias(col)
                for col in subset
                ])
            .unpivot(
                variable_name='column',
                value_name=freq
                )
            .filter(pl.col(freq) > 0)
            .sort(freq, descending=True)
            .collect()
            )

        if not null_counts.is_empty():
            raise ValueError(
                f'Nulls detected in {name}:\n\n{null_counts}'
                )

    elif null_policy == 'exclude':
        lf = lf.filter(
            pl.all_horizontal(
                pl.col(subset).is_not_null()
                )
            )

    dupe_counts = (
        lf
        .group_by(subset)
        .len()
        .filter(pl.col(freq) > 1)
        .sort(freq, descending=True)
        .select([*subset, freq])
        .collect()
        )

    if not dupe_counts.is_empty():
        raise ValueError(
            'Duplicates detected in '
            f'{name}:\n\n{dupe_counts}'
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

    validate_value(
        value=which,
        name='which',
        types=str,
        whitelist=['both','leading','trailing']
        )

    validate_value(
        value=how,
        name='how',
        types=str,
        whitelist=['any','all']
        )

    how_func = (
        pl.all_horizontal
        if how == 'any'
        else pl.any_horizontal
        )

    mask = how_func(pl.col(subset).is_not_null())

    not_leading = mask.cum_sum() > 0
    not_trailing = mask.reverse().cum_sum().reverse() > 0

    which_map = {
        'leading': not_leading,
        'trailing': not_trailing,
        'both': not_leading & not_trailing,
        }

    lf = lf.filter(which_map[which])

    # find a sample of rows where any subset column is null
    if not allow_nulls:

        sample = (
            lf
            .filter(
                pl.any_horizontal(
                    pl.col(subset)
                    .is_null()
                    )
                )
            .limit(5)
            .collect()
            )

        if not sample.is_empty():
            raise ValueError(
                'Remaining nulls detected in '
                f'{name}:\n\n{sample}'
                )

    return lf


@_preserve_input_type
def _purge_whitespace_with_polars(lf, subset, **kwargs):
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

    renames = {
        col: col.strip()
        for col in subset
        }

    new_subset = list(renames.values())

    lf = (
        lf
        .rename(renames)
        .with_columns(
            (cs.by_name(new_subset) & cs.string())
            .str.strip_chars().replace('', None)
            )
        .fill_nan(None)
        )

    return lf