from functools import wraps
import pandas as pd
import numpy as np

from ..iteration import ensure_list
from ..validation import validate_value


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


def purge_whitespace(func):
    ''' wrapper function that purges unwanted whitespace from a DataFrame '''

    @wraps(func)
    def wrapper(*args, **kwargs):

        def strip_or_skip(x):
            try:
                x = x.strip()
                if x == '':
                    return np.nan
            except:
                pass

            return x

        df = func(*args, **kwargs)

        # clean column names by trimming leading/trailing whitespace and
        # removing new lines and consecutive spaces
        renames = {
            k: ' '.join(k.split())
            for k in df.columns
            if isinstance(k, str)
            }

        df = df.rename(columns=renames)

        # replace None with np.nan
        for k in df.columns:
            try:
                df[k] = df[k].fillna(np.nan)
            except:
                pass

        # trim leading/trailing whitespace and replace whitespace-only values
        # with NaN
        for k in df.select_dtypes(include=['object']).columns:
            # df[k] = df[k].replace(
            #     to_replace=r'^\s*$',
            #     value=np.nan,
            #     regex=True
            #     )

            # using the vectorized string method str.strip() is faster but
            # object-type columns can have mixed data types
            df[k] = df[k].map(strip_or_skip) #.str.strip()

        # df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

        return df

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