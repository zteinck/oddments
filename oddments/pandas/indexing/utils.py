import pandas as pd

from ...validation import validate_value


def get_index_names(obj, simplify=False, drop_none=False):
    '''
    Description
    ------------
    Return the index name(s) of a pandas object.

    Parameters
    ------------
    obj : pd.DataFrame | pd.Series
        Object from which to retrieve index names.
    simplify : bool
        If True and the object does not have a MultiIndex, a single value is
            returned instead of a list. If the index is named, a string is
            returned, otherwise None.
        If False, a list is always returned.
    drop_none : bool
        If True, an empty list is returned if the index is unnamed.

    Returns
    ------------
    names : list | str | None
        Index name(s), depending on the 'simplify' argument.
    '''

    if simplify and drop_none:
        raise ValueError(
            "'simplify' and 'drop_none' arguments "
            "cannot both be True."
            )

    names = list(obj.index.names)
    n_levels = obj.index.nlevels

    if not names or n_levels == 0:
        raise ValueError(
            'Index must have at least one level?'
            )

    if len(names) != n_levels:
        raise ValueError(
            f'Length of index names ({len(names)}) does '
            f'not match number of levels ({n_levels}?'
            )

    all_none = all(name is None for name in names)

    if all_none and drop_none:
        return []

    if not all_none:
        for name in names:
            validate_value(
                value=name,
                name='index name',
                types=str,
                none_ok=False,
                empty_ok=False,
                )

    if simplify and len(names) == 1:
        return names[0]

    return names


def has_named_index(obj):
    ''' returns True if the object has a named index '''
    names = get_index_names(obj, drop_none=True)
    return len(names) > 0


def has_default_index(obj, ignore_name=True):
    '''
    Description
    ------------
    Returns True if a pandas object has the default index, otherwise False.

    Parameters
    ------------
    obj : pd.DataFrame | pd.Series
        Pandas object
    ignore_name :
        If the index has a single level, this parameter determines whether
        or not its name affects how the index is evaluated:
            • True: the index may still be considered default even if it has
                    a name.
            • False: the index is not considered default if its name is set
                     (i.e., not None).

    Returns
    ------------
    is_default : bool
        True if the index is considered default, otherwise False.
    '''
    names = get_index_names(obj)

    # MultiIndex or named index (when not ignored)
    if len(names) > 1 or (
        not ignore_name
        and names[0] is not None
        ):
        return False

    default_index = pd.RangeIndex(len(obj))
    return obj.index.equals(default_index)


def ensure_index_names(obj, name_template=None):
    '''
    Description
    ------------
    Ensures all index levels of the given object have names. Assigns default
    names to unnamed levels.

    Parameters
    ------------
    obj : pd.DataFrame | pd.Series
        Object for which index names will be ensured.
    name_template : str | None
        Serves as the default index name template if the given object does
        does not already have a named index. It should contain a placeholder
        for 'level'.

    Returns
    ------------
    out : pd.DataFrame | pd.Series
        Object with named index.
    '''
    obj = obj.copy(deep=True)

    if has_named_index(obj):
        return obj

    placeholder = '{level}'

    if name_template is None:
        name_template = 'level_' + placeholder

    if placeholder not in name_template:
        raise ValueError(
            f"'name_template' argument must include a {placeholder!r} "
            f"placeholder, got: {name_template!r}."
            )

    names = [
        name_template.format(**dict(level=level))
        for level in range(obj.index.nlevels)
        ]

    if len(names) == 1:
        obj.index.name = names[0]
    else:
        obj.index.names = names

    return obj