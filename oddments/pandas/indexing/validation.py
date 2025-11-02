from ...iteration import ensure_list
from ...validation import validate_value
from ..decorators import validate_pandas_objs
from .utils import get_index_names, has_named_index

_SENTINEL = object()


@validate_pandas_objs
def verify_index_names(objs, expected=_SENTINEL, none_ok=True):
    '''
    Description
    ------------
    Verifies that all given pandas objects have identical index names.

    Parameters
    ------------
    objs : array-like[pd.DataFrame | pd.Series]
        Array of pandas objects.
    expected : list | str | None
        Expected index name(s). If not provided, any index names are allowed
        as long as they are identical across all objects.
    none_ok : bool | None
        If False, an error is raised if any object has an unnamed index.
        Note: this parameter is ignored when 'expected' is provided.

    Returns
    ------------
    None
    '''
    has_expected = expected is not _SENTINEL

    if has_expected:
        expected = ensure_list(expected)

    for pos, obj in enumerate(objs):
        msg = f'Object at position {pos}'
        names = get_index_names(obj)

        if not (has_expected or none_ok or has_named_index(obj)):
            raise ValueError(
                f'{msg} is missing a named index, got: {names}.'
                )

        msg = f'{msg} has different index names than'

        if has_expected and names != expected:
            raise ValueError(
                f'{msg} expected: {names} vs {expected}.'
                )

        if pos > 0 and names != prior_names:
            raise ValueError(
                f'{msg} the previous object: '
                f'{names} vs {prior_names}.'
                )

        prior_names = names


def verify_index_values(obj):
    ''' verify index values do not contain NaNs '''
    for level, name in enumerate(list(obj.index.names)):
        if obj.index.get_level_values(name).isna().any():
            label = f'level {level}'
            if name is not None:
                label += f' ({name!r})'
            raise ValueError(
                f'NaNs detected in {label} index values.'
                )