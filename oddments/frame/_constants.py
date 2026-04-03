import polars as pl
import pandas as pd


POLARS_TYPES = (
    pl.LazyFrame,
    pl.DataFrame,
    pl.Series,
    )

PANDAS_TYPES = (
    pd.DataFrame,
    pd.Series,
    )