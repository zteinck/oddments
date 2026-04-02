import polars as pl
import pandas as pd

from ...validation import validate_value

from .._pandas import (
    _assert_unique_with_pandas,
    has_named_index
    )


def to_polars_frame(obj, name='obj', lazy=False):
    '''
    Description
    ------------
    Convert object to a Polars DataFrame or LazyFrame.

    Parameters
    ------------
    obj : pl.LazyFrame | (pl|pd).DataFrame | (pl|pd).Series
        Object to convert.
    name : str
        Optional name used to identify 'obj' in error messages.
    lazy : bool
        If True, a LazyFrame is returned; otherwise DataFrame.

    Returns
    ------------
    obj : pl.DataFrame | pl.LazyFrame
        LazyFrame if 'lazy=True', otherwise DataFrame.
    '''

    # validate object type
    polars_types = (
        pl.LazyFrame,
        pl.DataFrame,
        pl.Series,
        )

    pandas_types = (
        pd.DataFrame,
        pd.Series
        )

    validate_value(
        value=obj,
        name=name,
        types=polars_types + pandas_types
        )

    is_polars = isinstance(obj, polars_types)

    # create a copy of the object
    obj = (
        obj.clone()
        if is_polars
        else obj.copy(deep=True)
        )

    if is_polars and isinstance(obj, pl.LazyFrame):
        return obj if lazy else obj.collect()

    # convert Series to DataFrame
    if isinstance(obj, (pl.Series, pd.Series)):
        obj = obj.to_frame()

    if not is_polars:

        # verify column and index names are unique
        _assert_unique_with_pandas(
            obj,
            name=name,
            column_names=True,
            index_names=True,
            )

        # convert to polars DataFrame
        include_index = has_named_index(obj)

        obj = pl.from_pandas(
            data=obj,
            nan_to_null=True,
            include_index=include_index,
            )

    return obj.lazy() if lazy else obj


def to_polars_series(obj, name='obj'):
    '''
    Description
    ------------
    Convert object to a Polars Series.

    Parameters
    ------------
    Refer to 'to_polars_frame()' documentation.

    Returns
    ------------
    s : pl.Series
        Series object.
    '''

    df = to_polars_frame(obj=obj, name=name)

    if df.width != 1:
        raise ValueError(
            f'{name!r} must have exactly 1 column to be '
            f'converted to Series, got {df.width} columns.'
            )

    s = df.to_series()
    return s