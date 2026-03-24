import pandas as pd
import numpy as np

from .coercion import preserve_input_type


@preserve_input_type
def _purge_whitespace_with_pandas(df):

    def strip_or_skip(x):
        try:
            x = x.strip()
            if x == '':
                return np.nan
        except:
            pass

        return x


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
    for k in df.select_dtypes(
        include=['object','str']
        ).columns:
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


def columns_apply(df, func, inplace=False):
    '''
    Description
    ------------
    Applies a uniform function to all column names in a DataFrame.

    Parameters
    ------------
    df : pd.DataFrame
        dataframe to adjust column names
    func : func | str
        function to apply to each column name. If string, it will be
        interpreted as an attribute function of the column datatype
        (e.g. 'lower', 'upper', 'title', 'int', etc.).

    Returns
    ------------
    out : pd.DataFrame | None
        renamed dataframe is returned if inplace=False otherwise None
    '''
    renames = {
        k: func(k) if callable(func) else getattr(k, func)()
        for k in df.columns
        }
    return df.rename(columns=renames, inplace=inplace)


def column_name_is_datelike(name):
    ''' returns True if the given column name appears to represent a date,
        time, or both '''
    name = name.lower()
    word_match = any(word in name for word in ('date','time'))
    return word_match or name[-2:] == 'dt'


def infer_data_types(obj):
    ''' infers the appropriate data type for all columns in the DataFrame '''

    def preprocess_obj(obj):
        if isinstance(obj, pd.DataFrame):
            out = obj.copy(deep=True)
        elif isinstance(obj, pd.Series):
            out = obj.to_frame().copy(deep=True)
        else:
            raise TypeError(
                "'obj' argument type not supported: "
                f"{type(obj).__name__}"
                )
        return _purge_whitespace_with_pandas(out)


    df = preprocess_obj(obj)

    for k in df.columns:
        if column_name_is_datelike(k):
            try:
                df[k] = pd.to_datetime(df[k])
            except Exception as e:
                print(k, '→', e)
        else:
            try:
                df[k] = pd.to_numeric(df[k])
            except:
                pass

    return df