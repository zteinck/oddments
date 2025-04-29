

def iter_get(array, index=0, default=None):
    ''' extends dictionary's .get() to other iterables such as lists '''
    if array is None:
        return default
    try:
        return array[index]
    except IndexError:
        return default


def to_iter(x):
    ''' converts variable to a list '''
    return x if isinstance(x, (list, tuple)) else [x]


def delimit_iter(x, func=None, delimiter=', ', quotes='single', encase=True):
    '''
    Description
    ------------
    Delimits an iterable

    Parameters
    ------------
    x : iterable
        iterable to delimit
    func : type | func | None
        formats each element before it is delimited.
    delimiter : str
        delimiter
    quotes : str | None
        • 'single' ➜ encase each element in single quotes
        • 'double' ➜ encase each element in double quotes
        • None ➜ each element is not encased
    encase : bool
        if True, the final output is encased in parenthesis

    Returns
    ------------
    out : str
        delimited iterable
    '''
    if func is not None:
        x = list(map(func, x))

    x =  [f'{z}' for z in x]

    if quotes is not None:
        q = {'single': "'", 'double': '"'}[quotes]
        x =  [z.join([q] * 2) for z in x]

    x = delimiter.join(x)
    return f'({x})' if encase else x


def lower_iter(iterable):
    return [x.lower() for x in iterable]


def text_to_iter(text, transform=str, delimiter='\n'):
    '''
    Description
    ------------
    Converts a list of items in text format to a Python list.

    Parameters
    ------------
    text : str
        Delimited string
    transform : func
        Function applied to each item as list is constructed
    delimiter : str
        text delimiter

    Returns
    ------------
    out : list
        list if items in text file
    '''
    return [transform(x.strip()) for x in text.split(delimiter) if x.strip()]


def iter_window(
    x,
    left=0,
    right=0,
    strict=False,
    step=False,
    include_index=False
    ):
    '''
    iterates over a window of values in a list

    Parameters
    ----------
    x : list | other iterable
        list to iterate over
    left : int
        how many indices to the left of the current index to include in each
        returned slice
    right : int
        how many indices to the right of the current index to include in each
        returned slice
    strict : bool
        if True, only complete slices will be returned. (e.g. x=[1, 2, 3, 4, 5]
        and left=2 the first slice returned will be [1,2,3] at index 2. Index 0
        and 1 would be partial slices and not returned.
    step : bool
        if True, the right-most index of a slice will define the boundary line
        for the next slice so that no values repeat. (e.g. x=[1, 2, 3, 4, 5] and
        right=2 will return slices [1,2,3] and [4,5])
    include_index : bool
        if True, the index of the slice is also returned
    '''
    n, start = len(x) - 1, -1

    for i, v in enumerate(x):
        a, b = max(0, i - left), min(n, i + right)

        if step:
            if left > 0 and i == n: a = max(start, 0)
            if a < start: continue

        subset = x[ a : b + 1 ]
        if strict and len(subset) < left + right + 1: continue
        start = b + 1
        yield (i, subset) if include_index else subset