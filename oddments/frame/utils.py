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

        lib = (
            'polars'
            if isinstance(obj, POLARS_TYPES)
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