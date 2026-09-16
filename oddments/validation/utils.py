import polars as pl

from .validator import Validator


def sanitize_subset(
    subset,
    superset=None,
    subset_name='subset',
    superset_name='superset',
    ):
    '''
    Description
    ------------
    Sanitizes a subset of column names by ensuring it is a list of unique
    strings and optionally validates membership against a superset.

    Parameters
    ------------
    subset : None | str | array-like[str]
        Subset of column names. If None, the superset is returned.
    superset : None | str | array-like[str]
        Superset of column names.
    subset_name : str
        Subset name used in error messages.
    superset_name : str
        Superset name used in error messages.

    Returns
    ------------
    subset : list
        Sanitized subset of column names.
    '''

    def sanitize(value, name):

        (
        Validator(
            types=(str, list, tuple, set),
            allow_none=True,
            )
        .validate(value, name)
        )

        if value is None:
            return None

        if isinstance(value, str):
            return [value]

        s = pl.Series(
            name=name,
            values=value,
            dtype=str,
            strict=True,
            nan_to_null=True,
            )

        result = (
            s
            .drop_nulls()
            .unique(maintain_order=True)
            .to_list()
            )

        (
        Validator(
            types=list,
            allow_empty=False,
            )
        .validate(
            result,
            f'sanitized {name!r}',
            )
        )

        vd = Validator(
            types=str,
            allow_blank=False,
            # require_stripped=True, # messes up purge whitespace
            )

        for i, col in enumerate(result):
            vd.validate(col, f'at position {i}')

        return result


    subset = sanitize(subset, subset_name)
    superset = sanitize(superset, superset_name)

    if subset is None:
        return superset

    if superset is None:
        return subset

    whitelist = set(superset)

    extra_cols = [
        col for col in subset
        if col not in whitelist
        ]

    if extra_cols:
        raise ValueError(
            f'{subset_name} includes column names not found in '
            f'{superset_name}: {extra_cols}'
            )

    return subset