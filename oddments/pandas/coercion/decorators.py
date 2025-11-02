from functools import wraps
import pandas as pd

from .utils import (
    coerce_dataframe,
    coerce_series,
    coerce_ndim,
    )


def _coercion_handler(
    coercion_func,
    wrapped_func,
    *wrapped_args,
    preserve_ndim=False,
    **wrapped_kwargs
    ):
    '''
    Description
    ------------
    Enables coercion decorators to accommodate both standalone functions and
    instance methods. Note: static methods are not supported.

    Parameters
    ------------
    coercion_func : standalone function
        Coercion function
    wrapped_func : standalone function | instance method
        Decorated function
    wrapped_args : tuple
        Decorated function arguments
    wrapped_kwargs : dict
        Decorated function keyword arguments
    preserve_ndim : bool
        If True, the decorated function's return value is passed to
        coerce_ndim() before being returned to ensure it preserves
        the same dimensionality as the original data.

    Returns
    ------------
    out : pd.DataFrame | pd.Series | any
        Coerced data
    '''
    args = [*wrapped_args]
    kwargs = {**wrapped_kwargs}
    mods = []

    # if wrapped_func is an instance method then pop self from args
    if len(wrapped_func.__qualname__.split('.')) > 1:
        mods.append(args.pop(0))

    # identify data argument
    if args:
        data = args.pop(0)
    else:
        # user only passed kwargs
        kind = coercion_func.__name__.split('_')[-1]
        key = {'dataframe': 'df', 'series': 's'}[kind]
        data = kwargs.pop(key)

    # coerce data argument
    obj, ndim = coercion_func(
        data=data,
        return_ndim=True
        )

    mods.append(obj)
    args = mods + args
    out = wrapped_func(*args, **kwargs)

    if preserve_ndim:
        return coerce_ndim(out, ndim)

    return out


def with_coerce_series(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return _coercion_handler(
            coerce_series,
            func,
            *args,
            **kwargs
            )

    return wrapper


def with_coerce_dataframe(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return _coercion_handler(
            coerce_dataframe,
            func,
            *args,
            **kwargs
            )

    return wrapper


def preserve_input_type(func):

    @wraps(func)
    def wrapper(obj, *args, **kwargs):

        def check_if_series(obj):
            if isinstance(obj, pd.Series):
                return True
            elif isinstance(obj, pd.DataFrame):
                return False
            else:
                raise TypeError(
                    "Expected 'obj' argument to be a pandas Series "
                    f"or DataFrame, got: <{type(obj).__name__}>."
                    )

        is_series = check_if_series(obj)

        out = func(
            coerce_dataframe(obj),
            *args,
            **kwargs
            )

        if out is None:
            return

        coerce = (
            coerce_series
            if is_series
            else coerce_dataframe
            )

        return coerce(out)

    return wrapper