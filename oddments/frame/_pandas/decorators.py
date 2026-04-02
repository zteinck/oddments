from functools import wraps

import pandas as pd

from ...iteration import ensure_list
from ...validation import validate_value


def ignore_nan(func):
    ''' wrapper function that ignores np.nan arguments '''

    @wraps(func)
    def wrapper(arg, *args, **kwargs):
        return arg if pd.isna(arg) else func(arg, *args, **kwargs)

    return wrapper


def inplace_wrapper(func):
    ''' wrapper that adds inplace functionality to any function '''

    @wraps(func)
    def wrapper(obj, *args, **kwargs):

        if not kwargs.get('inplace', False):
            return func(obj.copy(deep=True), *args, **kwargs)

        func(obj, *args, **kwargs)

    return wrapper


def validate_pandas_objs(func):
    ''' Verifies that 'objs' argument is a non-empty list of pandas
        objects '''

    @wraps(func)
    def wrapper(objs, *args, **kwargs):
        objs = ensure_list(objs)

        if not objs:
            raise ValueError("'objs' cannot be empty.")

        for obj in objs:
            validate_value(
                value=obj,
                name='object',
                types=(pd.DataFrame, pd.Series)
                )

        return func(objs, *args, **kwargs)

    return wrapper