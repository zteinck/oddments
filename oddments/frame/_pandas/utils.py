import polars as pl
import pandas as pd

from .._polars import _purge_whitespace_with_polars
from .coercion import preserve_input_type
from .indexing import get_index_names


@preserve_input_type
def _purge_whitespace_with_pandas(df):
    index_names = get_index_names(df, drop_none=True)
    include_index = len(index_names) > 0

    df = pl.from_pandas(
        data=df,
        nan_to_null=True,
        include_index=include_index
        )

    df = _purge_whitespace_with_polars(df)
    df = df.to_pandas()

    if include_index:
        df = df.set_index(index_names)

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