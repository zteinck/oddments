from functools import wraps

from .utils import validate_value


def validate_setter(call_func=False, **kwargs):
    '''
    Description
    ------------
    Decorator for methods that are ultimately decorated by setters.
    Validates the value being set via validate_value().

    Parameters
    ------------
    call_func : bool
        If True, the wrapped function is called with self and value arguments
        passed. Otherwise, a protected attribute is set mirroring func's name.
        This parameter is useful for those scenarios where custom logic needs
        to be applied before setting the protected attribute.
    kwargs : dict
        keyword arguments passed to validate_value().

    Returns
    ------------
    None
    '''

    def decorator(func):

        @wraps(func)
        def wrapper(self, value):
            attr = func.__name__
            validate_value(attr=attr, value=value, **kwargs)
            if call_func: return func(self, value)
            setattr(self, '_' + attr, value)

        return wrapper

    return decorator