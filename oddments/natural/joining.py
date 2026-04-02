

def natural_join(items, operator='and'):
    '''
    Description
    ------------
    Joins a list of strings into a grammatically correct comma delimited line.

    Parameters
    ------------
    items : array-like[str] | str
        List of strings to join.

    Returns
    ------------
    joined : str
        Comma delimited list of items.

    Examples
    ------------
    • ['a'] → 'a'
    • ['a','b'] → 'a and b'
    • ['a','b','c'] → 'a, b, and c'
    '''

    if isinstance(items, str):
        return items

    count = len(items)

    if count == 0:
        raise ValueError(
            "'items' argument cannot be empty."
            )
    elif count == 1:
        return items[0]
    elif count == 2:
        return f' {operator} '.join(items)
    else:
        return f"{', '.join(items[:-1])}, {operator} {items[-1]}"