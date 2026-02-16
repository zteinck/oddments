from functools import wraps
import pandas as pd
import numpy as np

from ...validation import validate_value


def _validate_array_like(data):
    ''' raises an error if data is not array-like '''
    validate_value(
        value=data,
        name='data',
        types=(list, tuple, np.ndarray, pd.Index)
        )


def _get_data_dimensions(data):
    '''
    Description
    ------------
    Returns the number of dimensions of the input data. np.ndim returns:
        • 0 for single values (e.g. 'abc', 7, None)
        • 1 for flat (un-nested) array-like data (e.g. [], [1, 2, 3])
        • 2 for once nested array-like data (e.g. [[1, 3], [2, 4]]

    However, it will raise a value error on irregularly shaped array-like
    data such as jagged lists (e.g. [[1, 2], [0]]) that are otherwise still
    DataFrame compatible. This function handles such edge cases by
    attempting to return the maximum number of dimensions among the
    constituent elements of the input data.

    Parameters
    ------------
    data : any
        input data

    Returns
    ------------
    ndim : int
        Maximum number of dimensions of the input data.
    '''
    if isinstance(data, dict):
        ndim = min(max(len(data), 1), 2)

    elif isinstance(data, set):
        ndim = 1

    elif isinstance(data, pd.Index):
        ndim = min(data.nlevels, 2)

    else:
        try:
            ndim = np.ndim(data)
        except ValueError:
            _validate_array_like(data)
            ndim = max(np.ndim([x]) for x in data)

    return int(ndim)


def _apply_default_name(obj, default_name):
    '''
    Description
    ------------
    Applies default name(s) to pandas object if necessary.

    Parameters
    ------------
    obj : pd.DataFrame | pd.Series
        pandas object to which the default name will be applied.
    default_name : str | None
        Serves as the default Series name attribute or DataFrame column
        name(s) when the former is None or the latter is the default
        range of ascending integers. The name(s) will have a numeric
        suffix (e.g., '_0', '_1', ...) appended.
        if None, pandas' default name(s) are left intact.

    Returns
    ------------
    obj : pd.Series | pd.DataFrame
        renamed object
    '''
    validate_value(
        value=default_name,
        name='default_name',
        types=str,
        none_ok=True,
        empty_ok=False
        )

    if default_name is None:
        return obj

    # Unnamed Series
    if obj.ndim == 1 and obj.name is None:
        return obj.rename(default_name + '_0')

    # DataFrame with default integer column names
    if obj.ndim == 2 and all(
        isinstance(name, int) and name == index
        for index, name in enumerate(obj.columns)
        ):
        obj.columns = [
            f'{default_name}_{x}'
            for x in range(len(obj.columns))
            ]

    return obj


def _coercion_wrapper(func):

    @wraps(func)
    def wrapper(data, return_ndim=False, default_name='unnamed'):
        '''
        Description
        ------------
        Coerces data into a pandas DataFrame or Series.

        Parameters
        ------------
        data : any
            Data to be coerced to a Series or DataFrame.
            If 'data' is already of the desired type, a deep copy is
            returned.
        return_ndim : bool
            If True, the number of dimensions of the input data is returned.
        default_name : str | None
            see _apply_default_name() documentation

        Returns
        ------------
        out : pd.Series | pd.DataFrame
            Input data represented as a pandas object.
        ndim : int
            Only returned if 'return_ndim' is True.
        '''
        validate_value(
            value=return_ndim,
            name='return_ndim',
            types=bool,
            )

        ndim = _get_data_dimensions(data)

        if not 0 <= ndim <= 2:
            raise ValueError(
                f"Expected ndim to be ≤ 2, got: {ndim}. Invalid 'data' "
                f"argument of type <{type(data).__name__}>:\n\n{data}."
                )

        # sets are not compatible with pd.Series
        if isinstance(data, (set, range)):
            data = list(data)

        out = func(data, _ndim=ndim).copy(deep=True)
        out = _apply_default_name(out, default_name)
        return (out, ndim) if return_ndim else out

    return wrapper


@_coercion_wrapper
def coerce_series(data, _ndim):
    ''' coerce data to pd.Series '''

    if isinstance(data, pd.Series):
        return data

    elif isinstance(data, pd.DataFrame):
        n_cols = len(data.columns)
        if n_cols != 1:
            raise ValueError(
                'Only DataFrames with exactly 1 column may be '
                f'converted to Series, got {n_cols} columns.'
                )
        return data.iloc[:, 0]

    elif isinstance(data, dict):
        n_keys = len(data)
        if n_keys == 0: # empty dictionary
            return pd.Series()
        if n_keys != 1:
            raise ValueError(
                'Dictionary argument cannot have more '
                f'than 1 key, got {n_keys:,} keys.'
                )
        key, value = next(iter(data.items()))
        return coerce_series(value).rename(key)

    if _ndim == 0: # single value
        return pd.Series([data])

    elif _ndim == 1: # one-dimensional
        _validate_array_like(data)
        return pd.Series(data)

    raise ValueError(
        f"Expected ndim to be ≤ 1, got: {_ndim}. "
        f"Series coercion failed for 'data': {data}."
        )


@_coercion_wrapper
def coerce_dataframe(data, _ndim):
    ''' coerce data to pd.DataFrame '''

    if isinstance(data, pd.DataFrame):
        return data

    elif isinstance(data, pd.Series):
        return data.to_frame()

    elif isinstance(data, pd.Index):
        return data.to_frame(index=False)

    elif isinstance(data, dict) and len(data) > 0:
        objs = [
            coerce_series(v).rename(k)
            for k, v in data.items()
            ]
        return pd.concat(
            objs=objs,
            axis=1,
            join='outer'
            )

    if _ndim <= 1: # single value or one-dimensional
        return coerce_series(
            data=data,
            default_name=None
            ).to_frame()

    return pd.DataFrame(data)


def coerce_ndim(data, ndim):
    '''
    Description
    ------------
    Reshapes data to a desired number of dimensions. Useful for ensuring that
    transformed data preserves the same dimensionality as the original input.

    Parameters
    ------------
    data : any
        Data to be coerced to a DataFrame, Series, or scalar.
    ndim : int
        Desired number of dimensions. Supported optoins include:
            0: scalar
            1: pd.Series
            2: pd.DataFrame

    Returns
    ------------
    out : pd.DataFrame | pd.Series | any (scalar)
        Input data represented as a pandas object or scalar.
    '''
    validate_value(
        value=ndim,
        name='ndim',
        types=int
        )

    if not 0 <= ndim <= 2:
        raise NotImplementedError(
            f'Unsupported ndim={ndim}'
            )

    # two-dimensional ➜ DataFrame
    if ndim == 2:
        return coerce_dataframe(data)

    s = coerce_series(data)

    # one-dimensional ➜ Series
    if ndim == 1:
        return s

    # zero dimensions ➜ scalar
    if ndim == 0:
        if len(s) == 1:
            return s.iat[0]
        else:
            raise ValueError(
                'Cannot reduce series of length '
                f'{len(s):,} to scalar:\n\n{s}'
                )