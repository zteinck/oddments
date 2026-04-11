from functools import wraps

from ..validation import validate_value
from ._constants import *

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

        validate_value(
            value=obj,
            name='obj',
            types=POLARS_TYPES + PANDAS_TYPES,
            )

        keys = (
            'assert_unique',
            'purge_whitespace',
            'trim_nulls',
            )

        if isinstance(obj, POLARS_TYPES):
            values = (
                _assert_unique_with_polars,
                _purge_whitespace_with_polars,
                _trim_nulls_with_polars,
                )
        else:
            values = (
                _assert_unique_with_pandas,
                _purge_whitespace_with_pandas,
                _trim_nulls_with_pandas,
                )

        func_map = dict(zip(keys, values, strict=True))
        out = func_map[func.__name__](obj, *args, **kwargs)
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