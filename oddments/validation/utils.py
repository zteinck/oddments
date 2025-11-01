import numpy as np


def validate_value(
    value,
    types,
    name=None,
    finite=False,
    min_value=None,
    max_value=None,
    min_inclusive=False,
    max_inclusive=False,
    whitelist=None,
    blacklist=None,
    none_ok=False,
    empty_ok=True
    ):
    '''
    Description
    ------------
    Validates an an argument's type and value.

    Parameters
    ------------
    value : *
        argument to validate
    types : object | tuple
        one or more valid types of which value is allowed to be an instance.
    name : str | None
        Optional name of value to include in error messages. If None, 'value'
        is used.
    finite : bool
        if True, the value is not allowed to be -np.inf, +np.inf, np.nan, or
        any other value that would cause np.isfinite to return False.
    min_value : float | None
        minimum allowed value
    max_value : float | None
        maximum allowed value
    min_inclusive : bool
        if True, value is allowed to be equal to min_value (e.g. greater than
        or equal to)
    max_inclusive : bool
        if True, value is allowed to be equal to max_value (e.g. less than or
        equal to)
    whitelist : str | list
        list of acceptable values
    blacklist : str | list
        list of prohibited values
    none_ok : bool
        if True, None is an acceptable value and no further validation is
        necessary.
    empty_ok : bool
        if True, len(value) is allowed to be zero.

    Returns
    ------------
    None
    '''
    if none_ok and value is None:
        return

    if name is None:
        name = 'value'

    if not isinstance(types, tuple):
        types = (types,)

    if not isinstance(value, types):
        type_names = [f'<{x.__name__}>' for x in types]
        type_names = f"{', '.join(type_names[:-1])} or {type_names[-1]}" \
                     if len(type_names) > 1 else type_names[0]
        value_type = f'<{type(value).__name__}>'
        raise TypeError(
            f'{name!r} must be a {type_names}, '
            f'got: {value_type}.'
            )

    if blacklist is not None:
        if isinstance(blacklist, str):
            blacklist = [blacklist]
        if value in blacklist:
            raise ValueError(
                f'{name!r} cannot be in {blacklist}, '
                f'got: {value!r}.'
                )

    if whitelist is not None:
        if isinstance(whitelist, str):
            whitelist = [whitelist]

        typed_whitelist = [
            x for x in whitelist
            if isinstance(x, type(value))
            ]

        if typed_whitelist:
            if value in typed_whitelist:
                return

            raise ValueError(
                f'{name!r} must be in {whitelist}, '
                f'got: {value!r}.'
                )

    if not empty_ok and len(value) == 0:
        raise ValueError(
            f"{name!r} cannot be empty."
            )

    if finite:
        if not np.isfinite(value):
            raise TypeError(
                f'{name!r} must be finite, '
                f'got: {value!r}.'
                )

    msg = f"{name!r} must be {{0}} {{1}}, got: {value!r}"

    if min_value is not None:
        symbol = None
        if min_inclusive and value < min_value:
            symbol = '≥'
        if not min_inclusive and value <= min_value:
            symbol = '>'
        if symbol is not None:
            raise ValueError(msg.format(symbol, min_value))

    if max_value is not None:
        symbol = None
        if max_inclusive and value > max_value:
            symbol = '≤'
        if not max_inclusive and value >= max_value:
            symbol = '<'
        if symbol is not None:
            raise ValueError(msg.format(symbol, max_value))