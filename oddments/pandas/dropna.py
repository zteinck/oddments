import numpy as np

from .coercion import with_coerce_series
from .indexing import verify_index_monotonicity


@with_coerce_series
def trim_na(s, inf_as_na=False, raise_on_na=False):
    '''
    Description
    ------------
    Drops leading and trailing NaN values from a Series. Only Series with
    indexes sorted in ascending order are supported.

    Parameters
    ------------
    inf_as_na : bool
        If True, infinite values replaced with NaN.
    raise_on_na : bool
        If True, an error is raised if interior NaNs are present.

    Returns
    ------------
    out : pd.Series
       Series with leading and trailing NaN values dropped.
    '''

    verify_index_monotonicity(s, direction='increasing')

    if inf_as_na:
        s.replace(
            to_replace=[np.inf, -np.inf],
            value=np.nan,
            inplace=True
            )

    start = s.first_valid_index()
    stop = s.last_valid_index()
    out = s.loc[start:stop]

    if not raise_on_na or out.notna().all():
        return out

    msg = ['Series cannot contain NaN']
    if inf_as_na: msg.append('or Inf(+/-)')
    z = s.loc[(out[out.isna()].index)]
    msg.append(f'between valid values: \n\n{z}\n')
    raise ValueError(' '.join(msg))