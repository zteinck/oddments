from functools import cached_property
import re

from ..mixins import InitOnceMixin
from ..natural import natural_join
from ._engine import ValidationEngine


class Validator(InitOnceMixin):
    '''
    Description
    --------------------
    Encapsulates reusable validation criteria.

    Class Attributes
    --------------------
    None

    Instance Attributes
    --------------------
    _types : type | tuple[type]
        One or more acceptable types (i.e. classes).
    _class_mode : bool
        If True, values must be classes, otherwise instances.
    _whitelist : list | set
        List of acceptable values.
    _blacklist : list | set
        List of prohibited values.
    _pattern : re.Pattern
        Compiled regular expression string values must match.
    _min_value : any | None
        Minimum allowed value.
    _max_value : any | None
        Maximum allowed value.
    _min_inclusive : bool
        If True, values must be ≥ min_value.
        If False, values must be > min_value.
    _max_inclusive : bool
        If True, values must be ≤ max_value.
        If False, values must be < max_value.
    _allow_none : bool
        If True, None is an acceptable value.
    _allow_unset : bool
        If True, UNSET is an acceptable value.
    _allow_nan : bool
        If True, NaN is an acceptable value.
    _allow_empty : bool
        If True, values are permitted to be empty (i.e. len(value) == 0).
    _allow_blank : bool
        If False, string values must be neither empty nor whitespace-only.
    _allow_whitespace : bool
        If False, string values must not contain any whitespace.
    _require_stripped : bool
        If True, string values must not contain any leading or trailing
        whitespace. Interior whitespace is still permitted.
    _require_finite : bool
        If True, values must not be -inf, +inf, or NaN.
    _require_callable : bool
        If True, values must be callable.
    '''

    #╭-------------------------------------------------------------------------╮
    #| Initialize Instance                                                     |
    #╰-------------------------------------------------------------------------╯

    def __init__(
        self,
        types=None,
        class_mode=False,
        whitelist=None,
        blacklist=None,
        pattern=None,
        min_value=None,
        max_value=None,
        min_inclusive=False,
        max_inclusive=False,
        allow_none=False,
        allow_unset=False,
        allow_nan=False,
        allow_empty=True,
        allow_blank=True,
        allow_whitespace=True,
        require_stripped=False,
        require_finite=False,
        require_callable=False,
        ):

        # initialize boolean attributes from user parameters
        bool_params = {
            'class_mode': class_mode,
            'min_inclusive': min_inclusive,
            'max_inclusive': max_inclusive,
            'allow_none': allow_none,
            'allow_unset': allow_unset,
            'allow_nan': allow_nan,
            'allow_empty': allow_empty,
            'allow_blank': allow_blank,
            'allow_whitespace': allow_whitespace,
            'require_stripped': require_stripped,
            'require_finite': require_finite,
            'require_callable': require_callable,
            }

        for name, value in bool_params.items():
            if isinstance(value, bool):
                self._init_internal_attr(name, value)
            else:
                raise TypeError(
                    f'{name!r} must be a boolean, got '
                    f'{self._get_value_repr(value)}'
                    )

        self._types = self._normalize_types(types)
        self._pattern = self._normalize_pattern(pattern)
        self._min_value = min_value
        self._max_value = max_value

        for name, value in {
            'whitelist': whitelist,
            'blacklist': blacklist,
            }.items():
            value = self._normalize_lookup(name, value)
            self._init_internal_attr(name, value)

        self._validate_criteria()


    #╭-------------------------------------------------------------------------╮
    #| Instance Methods                                                        |
    #╰-------------------------------------------------------------------------╯

    def validate(self, *args, **kwargs):
        '''
        Description
        ------------
        Checks whether a given value satisfies the set of validation criteria.

        Parameters
        ------------
        args : tuple
            Positional arguments parsed as (value, name). Providing the second
            argument (i.e. 'name') is optional. If passed, a keyword argument
            must not be passed and vice versa.
        kwargs : dict
            A single key and value pair parsed as {name}={value}. If passed,
            positional arguments must not be passed and vice versa.

        Returns
        ------------
        None
        '''

        if not (bool(args) ^ bool(kwargs)):
            raise TypeError(
                'Must provide one or two positional values or exactly one '
                'keyword argument, not both or neither.'
                )

        if args:
            if len(args) == 1:
                value = args[0]
                name = None
            elif len(args) == 2:
                value, name = args
            else:
                raise ValueError(
                    'Expected one or two positional arguments, got '
                    f'{len(args):,}: {args}'
                    )
        elif kwargs:
            if len(kwargs) == 1:
                name, value = next(iter(kwargs.items()))
            else:
                raise ValueError(
                    'Expected exactly one keyword argument, got '
                    f'{len(kwargs):,}: {kwargs}'
                    )

        engine = ValidationEngine(
            validator=self,
            value=value,
            name=name,
            )

        engine.run()


    def _normalize_types(self, value):
        if value is None:
            return None

        if isinstance(value, (list, set, frozenset)):
            value = tuple(value)
        elif not isinstance(value, tuple):
            value = (value,)

        name = 'types'

        for i, v in enumerate(value):
            if not self._is_class(v):
                raise TypeError(
                    f'{name!r} item at position {i} must be a class, got: '
                    f'{v!r}'
                    )

        if not value:
            raise ValueError(
                f'{name!r} parameter cannot be empty.'
                )

        return value


    def _normalize_pattern(self, value):
        if value is None:
            return None

        if isinstance(value, re.Pattern):
            return value

        name = 'pattern'

        if not isinstance(value, str):
            raise TypeError(
                f'{name!r} must be a string or re.Pattern, got '
                f'{self._get_value_repr(value)}'
                )

        if not value.strip():
            raise ValueError(
                f'{name!r} must not be empty, got '
                f'{self._get_value_repr(value)}'
                )

        return re.compile(value)


    def _normalize_lookup(self, name, value):
        if value is None:
            return None

        types = (list, tuple, set, frozenset)

        if not isinstance(value, types):
            value_repr = self._get_value_repr(value)
            types_repr = self._get_types_repr(types)
            raise TypeError(
                f'{name!r} must be of type {types_repr} got {value_repr}'
                )

        items = self._try_to_set(value)

        if not self.has_types:
            return items

        for i, item in enumerate(items):
            self._check_type(item, f'{name!r} item at position {i}')

        return items


    def _get_instance_repr(self, value):
        type_repr = self._get_class_repr(type(value))
        return f'{type_repr}: {value!r}'


    def _get_value_repr(self, value):
        if self._is_class(value):
            return self._get_class_repr(value)
        else:
            return self._get_instance_repr(value)


    def _get_types_repr(self, types):
        items = [
            self._get_class_repr(cls)
            for cls in types
            ]

        text = natural_join(
            items=items,
            operator='or',
            )

        return text


    def _check_type(self, value, name):
        if self.class_mode:
            if not self._is_class(value):
                raise TypeError(
                    f'{name} must be a {self.mode} when class_mode=True, '
                    f'got {self._get_instance_repr(value)}'
                    )
            checker = issubclass
        else:
            checker = isinstance

        if self.types is None:
            return

        if not checker(value, self.types):
            raise TypeError(
                f'{name} must be a {self.types_repr} {self.mode}, got '
                f'{self._get_value_repr(value)}'
                )


    def _validate_criteria(self):

        reason_map = {
            "'class_mode' is True": self.class_mode,
            "<str> not in 'types'": (
                not self.has_types
                or str not in self.types
                ),
            }

        reasons = [k for k, v in reason_map.items() if v]

        if not reasons:
            return

        reason = reasons[0]

        for k, v in {
            'pattern': None,
            'allow_blank': True,
            'allow_whitespace': True,
            'require_stripped': False,
            }.items():

            value = getattr(self, k)

            if value != v:
                raise ValueError(
                    f'{k!r} must be {v!r} when {reason}.'
                    )


    #╭-------------------------------------------------------------------------╮
    #| Static Methods                                                          |
    #╰-------------------------------------------------------------------------╯

    @staticmethod
    def _is_class(value):
        ''' True if a given value is a class; otherwise False '''
        return isinstance(value, type)


    @staticmethod
    def _get_class_repr(cls):
        class_name = cls.__name__
        top_level = cls.__module__.split('.')[0]

        if top_level != 'builtins':
            class_name = f'{top_level}.{class_name}'

        return f'<{class_name}>'


    @staticmethod
    def _try_to_set(value):
        try:
            return set(value)
        except TypeError:
            return value


    #╭-------------------------------------------------------------------------╮
    #| Cached Properties                                                       |
    #╰-------------------------------------------------------------------------╯

    @cached_property
    def types_repr(self):
        if not self.has_types:
            return 'any type'
        return self._get_types_repr(self.types)



    #╭-------------------------------------------------------------------------╮
    #| Properties                                                              |
    #╰-------------------------------------------------------------------------╯

    @property
    def has_types(self):
        return self.types is not None


    @property
    def mode(self):
        return 'class' if self.class_mode else 'instance'


    @property
    def types(self):
        return self._types


    @property
    def class_mode(self):
        return self._class_mode


    @property
    def whitelist(self):
        return self._whitelist


    @property
    def blacklist(self):
        return self._blacklist


    @property
    def pattern(self):
        return self._pattern


    @property
    def min_value(self):
        return self._min_value


    @property
    def max_value(self):
        return self._max_value


    @property
    def min_inclusive(self):
        return self._min_inclusive


    @property
    def max_inclusive(self):
        return self._max_inclusive


    @property
    def allow_none(self):
        return self._allow_none


    @property
    def allow_unset(self):
        return self._allow_unset


    @property
    def allow_nan(self):
        return self._allow_nan


    @property
    def allow_empty(self):
        return self._allow_empty


    @property
    def allow_blank(self):
        return self._allow_blank


    @property
    def allow_whitespace(self):
        return self._allow_whitespace


    @property
    def require_stripped(self):
        return self._require_stripped


    @property
    def require_finite(self):
        return self._require_finite


    @property
    def require_callable(self):
        return self._require_callable