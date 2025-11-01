import re


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
        Sorted array.
    '''

    def alphanumeric_key(element):
        ''' converts string into a list of string and number chunks
            (e.g. 'z23a' -> ['z', 23, 'a']) '''

        def try_int(x):
            try:
                return int(x)
            except (ValueError, TypeError):
                return x

        parts = re.split(r'([0-9]+)', str(element))
        return list(map(try_int, parts))

    return sorted(array, key=alphanumeric_key)