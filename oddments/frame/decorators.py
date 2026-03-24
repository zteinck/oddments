from functools import wraps

from .utils import purge_whitespace


def apply_purge_whitespace(func):
    ''' decorator version of purge_whitespace '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        return purge_whitespace(func(*args, **kwargs))

    return wrapper