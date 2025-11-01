from ..validation import validate_value


def try_get(obj, index=0, default=None):
    '''
    Description
    ------------
    Like dict.get(), but works for any subscriptable object.

    Parameters
    ------------
    obj : any
        Object from which to get an element.
    index : int
        Position of the element as an integer index.
    default : any
        Value to return when an IndexError occurs.

    Returns
    ------------
    element : any
        Retrieved element
    '''
    validate_value(
        value=index,
        name='index',
        types=int
        )

    if obj is None:
        return default

    try:
        return obj[index]
    except IndexError:
        return default


def ensure_list(value):
    ''' ensures a value is a list '''
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def delimit_iterable(
    iterable,
    func=None,
    delimiter=', ',
    quotes='single',
    encase=True
    ):
    '''
    Description
    ------------
    Delimits an iterable.

    Parameters
    ------------
    iterable : any
        Iterable to delimit
    func : type | func | None
        Formats each element before it is delimited.
    delimiter : str
        String used to separate values.
    quotes : str | None
        • 'single' ➜ each element is encased in single quotes
        • 'double' ➜ each element is encased in double quotes
        • None ➜ No action is taken
    encase : bool
        If True, the return value is encased in parenthesis.

    Returns
    ------------
    delimited : str
        Delimited iterable
    '''
    if func is not None:
        iterable = list(map(func, iterable))

    iterable =  [f'{x}' for x in iterable]

    if quotes is not None:
        q = {'single': "'", 'double': '"'}[quotes]
        iterable =  [x.join([q] * 2) for x in iterable]

    iterable = delimiter.join(iterable)
    return f'({iterable})' if encase else iterable


def lower_iterable(iterable):
    return [x.lower() for x in iterable]


def text_to_iterable(text, transform=str, delimiter='\n'):
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
    return [
        transform(x.strip())
        for x in text.split(delimiter)
        if x.strip()
        ]


def iter_window(
    iterable,
    left=0,
    right=0,
    strict=False,
    step=False,
    include_index=False
    ):
    '''
    Description
    ------------
    Iterates over a window of values in a list.

    Parameters
    ----------
    iterable : any
        Object over which to iterate.
    left : int
        how many indices to the left of the current index to include in each
        returned slice
    right : int
        how many indices to the right of the current index to include in each
        returned slice
    strict : bool
        If True, only complete slices will be returned. (e.g. x=[1, 2, 3, 4, 5]
        and left=2 the first slice returned will be [1,2,3] at index 2. Index 0
        and 1 would be partial slices and not returned.
    step : bool
        if True, the right-most index of a slice will define the boundary line
        for the next slice so that no values repeat. (e.g. x=[1, 2, 3, 4, 5]
        and right=2 will return slices [1,2,3] and [4,5])
    include_index : bool
        if True, the index of the slice is also returned
    '''
    n, start = len(iterable) - 1, -1

    for i, v in enumerate(iterable):
        a, b = max(0, i - left), min(n, i + right)

        if step:
            if left > 0 and i == n: a = max(start, 0)
            if a < start: continue

        subset = iterable[ a : b + 1 ]
        if strict and len(subset) < left + right + 1: continue
        start = b + 1
        yield (i, subset) if include_index else subset