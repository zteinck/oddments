import numpy as np

from ..validation import validate_value
from .coercion import with_coerce_series
from .indexing import verify_index_values


@with_coerce_series
def trim_na(
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
    out : pd.Series
       Series without leading and/or trailing null values.
    '''

    validate_value(
        value=which,
        name='which',
        types=str,
        whitelist=['both','leading','trailing']
        )

    verify_index_values(s)

    if s.empty:
        return s

    out = s.copy(deep=True)

    if inf_as_na:
        out.replace(
            to_replace=[np.inf, -np.inf],
            value=np.nan,
            inplace=True
            )

    if out.isna().all():
        if raise_on_na:
            raise ValueError(
                'Series only contains nulls.'
                )
        return out.dropna()

    first = out.first_valid_index()
    last = out.last_valid_index()

    bounds = {
        'both': (first, last),
        'leading': (first, None),
        'trailing': (None, last),
        }

    left, right = bounds[which]
    out = out.loc[left:right]

    valid = out.notna()

    if not raise_on_na or valid.all():
        return out

    nulls = s.loc[(out[(~valid)].index)]

    raise ValueError(
        f'Series contains nulls:\n\n{nulls}\n'
        )