import pandas as pd

from ..validation import validate_value
from .decorators import validate_pandas_objs
from .dupes import verify_unique

from .indexing import (
    get_index_names,
    has_named_index,
    verify_index_names,
    )


def _prep_merge_params(kwargs, _join):
    '''
    Description
    ------------
    Validates and standardizes merge parameters.

    Parameters
    ------------
    See 'merge' function documentation.

    Returns
    ------------
    params : dict
        Prepped merge parameters.
    '''
    params = {**kwargs}

    # set default 'how' parameter
    params.setdefault('how', 'left')

    # set left and right index parameters
    for key in ['left_index','right_index']:
        if key in params:
            raise TypeError(
                f'{key!r} parameter is set automatically '
                'and cannot be passed by the user.'
                )
        if _join:
            params[key] = True

    # validate and format join key parameters
    keys = ('on', 'left_on', 'right_on')

    for key in keys:
        if key in params:
            if _join:
                raise TypeError(
                    f'{key!r} parameter cannot be passed during '
                    'join operations, only during merge.'
                    )

            value = params[key]

            validate_value(
                value=value,
                name=key,
                types=(list, str),
                none_ok=True,
                empty_ok=False,
                )

            params[key] = (
                [value]
                if isinstance(value, str)
                else sorted(set(value))
                )

    if not _join:
        on = params.pop(keys[0], None)

        for key in keys[1:]:
            value = params.get(key, None)
            msg = repr(key) + " {0} be None if 'on' {1} None."

            if on is None:
                if value is None:
                    raise TypeError(
                        msg.format('cannot', 'is')
                        )
            else:
                if value is None:
                    params[key] = on
                else:
                    raise TypeError(
                        msg.format('must', 'is not')
                        )

    return params


def _merge(left, right, _join, **kwargs):
    '''
    Description
    ------------
    Merges 'left' and 'right' DataFrames.

    Parameters
    ------------
    left : pd.DataFrame
        Left object to merge.
    right : pd.DataFrame
        Right object to merge.

    Returns
    ------------
    df : pd.DataFrame
        'left' and 'right' objects merged.
    '''
    params = {**kwargs}

    # account for anti-joins
    is_anti = params['how'] == 'anti'

    if is_anti:
        params.update({'how': 'left', 'indicator': True})
        right = right[[] if _join else params['right_on']]

    left_cols, right_cols = (
        obj.columns.tolist()
        for obj in (left, right)
        )

    if not _join:
        left_on, right_on = (
            set(params[key]) for key in
            ('left_on', 'right_on')
            )

        shared_keys = left_on.intersection(right_on)
        right_keys = right_on.difference(left_on)

        if shared_keys:
            right_cols = [
                x for x in right_cols
                if x not in shared_keys
                ]

    verify_unique(
        pd.Series(left_cols + right_cols, name='name'),
        label='left & right column name',
        column_values=True,
        )

    # merge 'left' and 'right' DataFrames
    df = left.merge(right, **params)

    # handle anti-join
    if is_anti:
        key = '_merge'
        df = df[(df[key] == 'left_only')]
        if not kwargs.get('indicator', False):
            df = df.drop(columns=key)

    # drop 'right_on' columns from the merge result
    if not _join and right_keys:
        df = df.drop(columns=right_keys, errors='ignore')

    return df


def merge(objs, _join=False, **kwargs):
    '''
    Description
    ------------
    Wrapper around pandas.merge that provides several quality-of-life
    enhancements:
        • Supports merging more than two pandas objects at a time.
        • Ensures the index of the left-most pandas object is preserved.
        • Checks for duplicate column names to prevent unexpected behavior.
        • Offers 'left_dupes_ok' and 'right_dupes_ok' arguments.
        • 'how' argument:
            - Defaults to 'left' instead of 'inner'.
            - Supports 'anti' joins (returns rows in 'left' not present in
              'right').

    Parameters
    ------------
    objs : array-like[pd.DataFrame | pd.Series]
        Array of pandas objects.
    _join : bool
        If True, join on index.
    left_dupes_ok : bool
        If True, the left-most object's join keys are allowed to contain
        duplicates; otherwise an error is raised.
    right_dupes_ok : bool
        If True, the join keys of objects to the right of the left-most
        object are allowed to contain duplicates; otherwise an error is
        raised.
    kwargs : dict
        Keyword arguments.

    Returns
    ------------
    df : pd.DataFrame
        Merged objects
    '''
    params = _prep_merge_params(kwargs, _join)
    restore_index = not _join and has_named_index(objs[0])
    index_names = get_index_names(objs[0], simplify=True)

    df = None
    dupes_ok = {}

    for pos, obj in enumerate(objs):
        label = 'left' if pos == 0 else 'right'

        if isinstance(obj, pd.Series):
            obj = obj.to_frame()

        obj = obj.copy(deep=True)

        if not _join:
            join_keys = params[f'{label}_on']
            if has_named_index(obj):
                obj.reset_index(inplace=True)

        if label not in dupes_ok:
            key = f'{label}_dupes_ok'
            if _join and key in params:
                raise NotImplementedError(
                    f'{key!r} parameter is not supported for '
                    'join operations, only during merge.'
                    )
            dupes_ok[label] = params.pop(key, not _join)

        subset = (
            False
            if _join or dupes_ok[label]
            else join_keys[:]
            )

        verify_unique(
            obj=obj,
            label=label,
            column_names=True,
            column_values=subset,
            index_names=True,
            index_values=_join and not dupes_ok[label],
            include_index=False,
            dropna=False,
            )

        df = obj if df is None else \
            _merge(
                left=df,
                right=obj,
                _join=_join,
                **params
                )

    if restore_index:
        df.set_index(index_names, inplace=True)

    verify_index_names(df, index_names)
    return df


@validate_pandas_objs
def join(objs, **kwargs):
    '''
    Description
    ------------
    Merge one or more pandas objects using their index. See 'merge' function
    documentation for more information.

    Parameters
    ------------
    objs : array-like[pd.DataFrame | pd.Series]
        Array of pandas objects.
    kwargs : dict
        Keyword arguments.

    Returns
    ------------
    df : pd.DataFrame
        Joined objects
    '''
    verify_index_names(objs, none_ok=True)
    df = merge(objs, _join=True, **kwargs)
    return df


@validate_pandas_objs
def concat(objs, **kwargs):
    '''
    Description
    ------------
    Alternative to pandas' 'pd.concat' function that offers several
    quality-of-life enhancements:
        • Ensures the index name of the left-most pandas object is preserved
          when 'ignore_index=False'.
        • If 'ignore_index' keyword argument is not provided or None, an
          appropriate value is inferred.
        • Allows 'how' to be used in place of pd.concat's 'join' keyword
          argument for consistency with merge and join functions.

    Parameters
    ------------
    objs : array-like[pd.DataFrame | pd.Series]
        Array of pandas objects.
    kwargs : dict
        Keyword arguments.

    Returns
    ------------
    df : pd.DataFrame
        Concatenated objects
    '''
    params = {**kwargs}

    if 'how' in params:
        if 'join' in params:
            raise ValueError(
                "Cannot specify both 'how' and 'join'."
                )
        params['join'] = params.pop('how')

    defaults = dict(axis=0, join='outer')

    for key, default in defaults.items():
        params.setdefault(key, default)

    verify_index_names(objs, none_ok=True)
    index_names = get_index_names(objs[0])

    key = 'ignore_index'
    if params.get(key) is None:
        params[key] = (
            not has_named_index(objs[0])
            if params['axis'] == 0
            else False
            )

    df = pd.concat(objs, **params)

    # verify index name(s) were preserved
    if not params[key]:
        verify_index_names(df, index_names)

    return df