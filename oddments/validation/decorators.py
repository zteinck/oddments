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
            name = func.__name__
            validate_value(value=value, name=name, **kwargs)
            if call_func: return func(self, value)
            setattr(self, '_' + name, value)

        return wrapper

    return decorator