import re

_RE_DIGITS = re.compile(r'([0-9]+)')


def _natural_sort_key(element):
    '''
    Description
    ------------
    Splits the string representation of an element into a list of numeric and
    non-numeric tokens. (e.g. 'z23a' → ['z', 23, 'a'])

    Parameters
    ------------
    element : any
        Array element.

    Returns
    ------------
    tokens : list
        Sequence of alphanumeric tokens where numeric substrings are cast as
        integers.
    '''

    parts = _RE_DIGITS.split(str(element))
    tokens = [int(x) if x.isdigit() else x for x in parts]
    return tokens


def natural_sort(array):
    '''
    Description
    ------------
    Sorts list via natural sorting as opposed to lexicographical sorting.
    For example, consider a list of file names starting with numbers
    ['101 Dalmatians.xlsx', '3 Blind Mice.xlsx']. Sorting using the default
    method will yield the same list because the first character "1" < "3".
    Conversely, natural sorting will intuitively place the name beginning
    with "3" before "101" since "3" < "101".

    Parameters
    ------------
    array :  array-like
        Array to sort naturally.

    Returns
    ------------
    sorted : array-like
        Naturally sorted array.
    '''

    return sorted(array, key=_natural_sort_key)