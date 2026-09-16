from functools import wraps

from .validator import Validator


def validate_on_set(call_wrapped=False, **kwargs):
    '''
    Description
    ------------
    Decorator for methods that are ultimately decorated by setters.
    Validates the value being set via Validator().

    Parameters
    ------------
    call_wrapped : bool
        If True, the wrapped function is called with self and value arguments
        passed. Otherwise, a protected attribute is set mirroring func's name.
        This parameter is useful for those scenarios where custom logic needs
        to be applied before setting the protected attribute.
    kwargs : dict
        keyword arguments passed to Validator().

    Returns
    ------------
    None
    '''

    def decorator(func):

        @wraps(func)
        def wrapper(self, value):
            name = func.__name__
            Validator(**kwargs).validate(value, name)

            if call_wrapped:
                return func(self, value)

            setattr(self, '_' + name, value)

        return wrapper

    return decorator