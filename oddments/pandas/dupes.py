from functools import wraps
import pandas as pd

from ..validation import validate_value
from .coercion import preserve_input_type

from .indexing import (
    has_default_index,
    has_named_index,
    get_index_names,
    verify_index_values,
    )


def _resolve_include_index(func):

    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        params = {**kwargs}
        key = 'include_index'
        value = params.get(key, False)

        if value and has_default_index(obj):
            value = False

        if value and not has_named_index(obj):
            raise NotImplementedError(
                'Support for including unnamed '
                'index is not yet implemented.'
                )

        params[key] = value
        return func(obj, *args, **params)

    return wrapper


@preserve_input_type
@_resolve_include_index
def drop_duplicates(df, **kwargs):
    '''
    Description
    ------------
    Alternative to pandas' drop_duplicates() that optionally considers the
    index.

    Parameters
    ------------
    obj : pd.DataFrame | pd.Series
        Pandas object to inspect for duplicates.
    include_index : bool
        If True, duplicate detection considers both the index and row values,
        rather than just the row values.
    kwargs : dict
        Keyword arguments passed to the native method.

    Returns
    ------------
    out : pd.DataFrame | pd.Series
        Pandas object with duplicates removed.
    '''
    params = {**kwargs}

    key = 'inplace'
    if params.get(key, False):
        raise ValueError(
            f"The {key!r} parameter is not supported."
            )

    include_index = params.pop('include_index')

    if include_index:
        index_names = get_index_names(df, simplify=True)
        df = df.reset_index()

    df = df.drop_duplicates(**params)

    if include_index:
        df = (
            df.drop(columns=index_names)
            if params.get('ignore_index')
            else df.set_index(index_names)
            )

    return df


@preserve_input_type
@_resolve_include_index
def verify_unique(
    df,
    label=None,
    column_names=True,
    column_values=False,
    index_names=True,
    index_values=False,
    dropna=False,
    show_top=10,
    **kwargs
    ):
    '''
    Description
    ------------
    Raises an error if duplicates are found.

    Parameters
    ------------
    obj : pd.DataFrame | pd.Series
        Pandas object to inspect for duplicates.
    label : str | None
        Display name for error messages.
    column_names : bool
        If True, check for duplicates among the column names.
    column_values : bool
        • If True, check for duplicate rows.
        • If list, include only the specified columns.
        • If str, include a single column.
    index_names : bool
        If True, check for duplicates among the names of the index
        levels and for conflicts with column names.
    index_values : bool
        If True, check for duplicates and NaNs among the values in the index.
    include_index : bool
        If True and column_values is not False, duplicate detection considers
        both index and column values.
    dropna : bool
        If False, NaN values are considered when identifying duplicates in
        column values.
    show_top : int | None
        If int, the maximum number of duplicates that may be included
        in the error message.

    Returns
    ------------
    None
    '''

    def check(obj, msg):
        if isinstance(obj, list):
            obj = pd.Series(obj)

        if len(obj) < 2: return
        s = obj.value_counts(dropna=False)

        dupes = s[(s > 1)]
        if dupes.empty: return

        if show_top is not None \
            and show_top < len(dupes):
            dupes = dupes.head(show_top)
            msg = f'{msg} (top {show_top} showing)'

        dupes = dupes.to_frame()
        raise ValueError(f'{msg}:\n\n{dupes}\n')


    # default label
    if label is None:
        label = 'df'

    # standard error message verbiage
    msg = f'Duplicates detected in {label}'

    # check for invalid column names (NaN or None)
    if df.columns.isna().any():
        raise ValueError(
            f'NaNs detected in {label} column names.'
            )

    # check for duplicate column names
    col_names = df.columns.tolist()

    if column_names:
        check(col_names, f'{msg} column names')

    if index_names:
        # retrieve index names
        idx_names = get_index_names(df, drop_none=True)

        if idx_names:
            # check for duplicate index names
            check(idx_names, f'{msg} index names')

            # check for conflicts between index and column names
            check(
                idx_names + col_names,
                f'Conflicts detected between {label} '
                'index and column names'
                )

    if index_values:
        # check for invalid index values (NaN or None)
        verify_index_values(df)

        # check for duplicate index values
        # using mask to make value_counts more efficient
        mask = df.index.duplicated(keep=False)
        check(df.index[mask], f'{msg} index values')

    if df.empty: return

    if isinstance(column_values, bool):
        if not column_values: return
        subset = df.columns.tolist()
    elif isinstance(column_values, str):
        subset = [column_values]
    else:
        validate_value(column_values, list)
        subset = column_values[:]

    for k in subset:
        validate_value(k, name='column', types=str)

    df = df[subset]

    if kwargs['include_index']:
        df = df.reset_index()

    if dropna:
        df = df.dropna()
        if df.empty: return

    # using mask to make value_counts more efficient
    mask = df.duplicated(keep=False)
    check(df[mask], f'{msg} values')