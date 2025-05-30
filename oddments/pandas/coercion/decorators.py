from functools import wraps

from .utils import (
    coerce_dataframe,
    coerce_series
    )


def _coercion_handler(func, coerce, *args, **kwargs):
    '''
    Description
    ------------
    Function that enables coercion decorators to accommodate both standalone
    functions and instance methods.

    Note: does not work with static methods.

    Parameters
    ------------
    func : func
        decorated function
    coerce : func
        coercion function
    args : tuple
        func arguments
    kwargs : dict
        func keyword arguments

    Returns
    ------------
    out : pd.DataFrame | pd.Series
        coercion function output
    '''
    if not args:
        # user only passed kwargs
        kind = coerce.__name__.split('_')[-1]
        key = {'dataframe': 'df', 'series': 's'}[kind]
        args = (kwargs.pop(key),)

    if len(func.__qualname__.split('.')) > 1:
        # func is an instance method
        self, arg = args[0], coerce(args[1])
        return func(self, arg, *args[2:], **kwargs)
    else:
        # func is a standalone function
        arg = coerce(args[0])
        return func(arg, *args[1:], **kwargs)


def with_series_coercion(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return _coercion_handler(func, coerce_series, *args, **kwargs)

    return wrapper


def with_dataframe_coercion(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return _coercion_handler(func, coerce_dataframe, *args, **kwargs)

    return wrapper