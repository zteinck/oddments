from functools import wraps

from ..validation import Validator
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

        (
        Validator(
            types=(POLARS_TYPES + PANDAS_TYPES)
            )
        .validate(
            obj=obj
            )
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
        result = func_map[func.__name__](obj, *args, **kwargs)
        return result

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