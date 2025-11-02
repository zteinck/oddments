import pandas as pd

from .decorators import purge_whitespace


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

    @purge_whitespace
    def preprocess_obj(obj):
        if isinstance(obj, pd.DataFrame):
            return obj.copy(deep=True)
        elif isinstance(obj, pd.Series):
            return obj.to_frame().copy(deep=True)
        else:
            raise TypeError(
                "'obj' argument type not supported: "
                f"{type(obj).__name__}"
                )

    df = preprocess_obj(obj)

    for k in df.columns:
        if column_name_is_datelike(k):
            try:
                df[k] = pd.to_datetime(df[k])
            except Exception as e:
                print(k, '➜', e)
        else:
            try:
                df[k] = pd.to_numeric(df[k])
            except:
                pass

    return df