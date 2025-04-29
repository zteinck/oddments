import re


def natural_sort(array, inplace=False):
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
    array :  list
        list to sort
    inplace : bool
        if True, sorting will be done inplace

    Returns
    ------------
    out : list | None
        list if inplace is False otherwise None
    '''

    def alphanumeric_key(element):
        ''' converts string into a list of string and number chunks
            (e.g. 'z23a' -> ['z', 23, 'a']) '''

        def try_int(x):
            try:
                return int(x)
            except:
                return x

        out = list(map(try_int, re.split('([0-9]+)', str(element))))
        return out

    if inplace:
        array.sort(key=alphanumeric_key)
    else:
        return sorted(array, key=alphanumeric_key)