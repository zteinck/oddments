from functools import wraps
import pandas as pd
import numpy as np


def ignore_nan(func):
    ''' wrapper function that ignores np.nan arguments '''

    @wraps(func)
    def wrapper(arg, *args, **kwargs):
        if pd.notnull(arg):
            return func(arg, *args, **kwargs)
        else:
            return arg

    return wrapper


def inplace_wrapper(func):
    ''' wrapper that adds inplace functionality to any function '''

    @wraps(func)
    def wrapper(df, *args, **kwargs):
        inplace = kwargs.get('inplace', False)

        if inplace:
            func(df, *args, **kwargs)
        else:
            return func(df.copy(deep=True), *args, **kwargs)

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

        # clean column names by trimming leading/trailing whitespace and removing
        # new lines and consecutive spaces
        renames = {k: ' '.join(k.split()) for k in df.columns if isinstance(k, str)}
        df.rename(columns=renames, inplace=True)

        # replace None with np.nan
        for k in df.columns:
            try:
                df[k] = df[k].fillna(np.nan)
            except:
                pass

        # trim leading/trailing whitespace and replace whitespace-only values with NaN
        for k in df.select_dtypes(include=['object']).columns:
            # df[k] = df[k].replace(to_replace=r'^\s*$', value=np.nan, regex=True)

            # using the vectorized string method str.strip() is faster but object-type
            # columns can have mixed data types
            df[k] = df[k].apply(strip_or_skip) #.str.strip()

        # df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

        return df

    return wrapper