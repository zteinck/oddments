import numpy as np

from ...validation import Validator
from .coercion import apply_to_pandas_series
from .indexing import verify_index_values


@apply_to_pandas_series
def _trim_nulls_with_pandas(
    s,
    which='both',
    inf_as_na=False,
    raise_on_na=False,
    ):
    '''
    Description
    ------------
    Drops leading and/or trailing null values from a Series.

    Parameters
    ------------
    which : str
        Specifies which null values to drop:
            • 'both' → Drop both leading and trailing nulls.
            • 'leading' → Drop only leading nulls.
            • 'trailing' → Drop only trailing nulls.
    inf_as_na : bool
        If True, infinite values replaced with NaN.
    raise_on_na : bool
        If True, an error is raised if any null values remain.

    Returns
    ------------
    result : pd.Series
       Series without leading and/or trailing null values.
    '''

    (
    Validator(
        types=str,
        whitelist=['both','leading','trailing']
        )
    .validate(
        which=which
        )
    )

    verify_index_values(s)

    if s.empty:
        return s

    result = s.copy(deep=True)

    if inf_as_na:
        result.replace(
            to_replace=[np.inf, -np.inf],
            value=np.nan,
            inplace=True
            )

    if result.isna().all():
        if raise_on_na:
            raise ValueError(
                'Series only contains nulls.'
                )
        return result.dropna()

    first = result.first_valid_index()
    last = result.last_valid_index()

    bounds = {
        'both': (first, last),
        'leading': (first, None),
        'trailing': (None, last),
        }

    left, right = bounds[which]
    result = result.loc[left:right]

    valid = result.notna()

    if not raise_on_na or valid.all():
        return result

    nulls = s.loc[(result[(~valid)].index)]

    raise ValueError(
        f'Series contains nulls:\n\n{nulls}\n'
        )