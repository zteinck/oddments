from functools import wraps
import pandas as pd
import polars as pl

from ..validation import validate_value

from ._pandas import (
    _assert_unique_with_pandas,
    _purge_whitespace_with_pandas,
    _trim_nulls_with_pandas,
    )

from ._polars import (
    _assert_unique_with_polars,
    _purge_whitespace_with_polars,
    _trim_nulls_with_polars,
    )


def _dispatch(func):

    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        polars_types = (pl.DataFrame, pl.Series, pl.LazyFrame)
        pandas_types = (pd.DataFrame, pd.Series)

        validate_value(
            value=obj,
            name='obj',
            types=polars_types + pandas_types,
            )

        lib = (
            'polars'
            if isinstance(obj, polars_types)
            else 'pandas'
            )

        func_name = f'_{func.__name__}_with_{lib}'
        out = globals()[func_name](obj, *args, **kwargs)
        return out

    return wrapper


@_dispatch
def assert_unique():
    pass


@_dispatch
def purge_whitespace():
    pass


@_dispatch
def trim_nulls():
    pass