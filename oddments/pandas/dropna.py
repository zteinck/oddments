import numpy as np

from .coercion import with_coerce_series


@with_coerce_series
def dropna_edges(s, drop_inf=False, ignore_gaps=False):
    '''
    Description
    ------------
    Drops leading and trailing NaN values in a Series. Only Series with
    indexes sorted in ascending order are supported.

    Parameters
    ------------
    drop_inf : bool
        If True, infinite values replaced with NaN
    ignore_gaps : bool
        If True, NaN values exist between valid values are permitted.
        If False, if any NaN values exist between valid values, an exception
            is raised.

    Returns
    ------------
    out : pd.Series
       Series with leading and trailing NaN values dropped.
    '''

    if not s.index.is_monotonic_increasing:
        raise NotImplementedError(
            "'s' argument's index must be "
            "sorted in ascending order."
            )

    if drop_inf:
        s.replace(
            to_replace=[np.inf, -np.inf],
            value=np.nan,
            inplace=True
            )

    first_index = s.first_valid_index()
    last_index = s.last_valid_index()

    out = s.loc[first_index:last_index]

    if ignore_gaps or out.notna().all():
        return out

    msg = ["'s' argument cannot contain NaN"]
    if drop_inf: msg.append('or Inf(+/-)')
    z = s.loc[(out[out.isna()].index)]
    msg.append(f"between valid values: \n\n{z}\n")
    raise ValueError(' '.join(msg))