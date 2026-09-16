from functools import cached_property

import numpy as np
import pandas as pd

from ..sentinels import UNSET


class ValidationEngine:
    '''
    Description
    --------------------
    Validates a value against specified criteria.

    Class Attributes
    --------------------
    None

    Instance Attributes
    --------------------
    _validator : Validator
        Validator instance.
    _value : any
        Value to validate.
    _name : str
        The name or description of the value to use in error messages if
        validation fails.
    '''

    #╭-------------------------------------------------------------------------╮
    #| Initialize Instance                                                     |
    #╰-------------------------------------------------------------------------╯

    def __init__(self, validator, value, name):
        self._validator = validator
        self._value = value
        self._name = self._normalize_name(name)


    #╭-------------------------------------------------------------------------╮
    #| Magic Methods                                                           |
    #╰-------------------------------------------------------------------------╯

    def __getattr__(self, name):
        return getattr(self._validator, name)


    #╭-------------------------------------------------------------------------╮
    #| Properties                                                              |
    #╰-------------------------------------------------------------------------╯

    @property
    def name(self):
        return self._name


    @property
    def value(self):
        return self._value


    #╭-------------------------------------------------------------------------╮
    #| Cached Properties                                                       |
    #╰-------------------------------------------------------------------------╯

    @cached_property
    def value_type(self):
        return self.value if self.class_mode else type(self.value)


    @cached_property
    def value_repr(self):
        return self._get_value_repr(self.value)


    @cached_property
    def effective_blacklist(self):
        return self._to_effective_list(self.blacklist)


    @cached_property
    def effective_whitelist(self):
        return self._to_effective_list(self.whitelist)


    @cached_property
    def is_string(self):
        return isinstance(self.value, str)


    #╭-------------------------------------------------------------------------╮
    #| Instance Methods                                                        |
    #╰-------------------------------------------------------------------------╯

    def run(self):

        # early return conditions
        if any((
            (self.allow_none and self.value is None),
            (self.allow_unset and self.value is UNSET),
            (self.allow_nan and pd.isnull(self.value))
            )):
            return

        self._assert_callable()
        self._assert_type_or_subclass()
        self._assert_not_blacklisted()
        self._assert_whitelisted()
        self._assert_not_empty()
        self._assert_stripped()
        self._assert_not_blank()
        self._assert_not_whitespace()
        self._assert_matches_pattern()
        self._assert_finite()
        self._assert_meets_minimum()
        self._assert_meets_maximum()


    def _normalize_name(self, value):
        if value is None:
            return repr('value')

        name = 'name'
        value_repr = self._get_instance_repr(value)

        if not isinstance(value, str):
            raise TypeError(
                f'{name!r} must be a string, got {value_repr}'
                )

        value = value.strip()

        if not value:
            raise ValueError(
                f'{name!r} cannot be blank.'
                )

        if len(value.split()) == 1:
            return repr(value)

        return value


    def _assert_callable(self):
        if self.require_callable and not callable(self.value):
            raise TypeError(
                f'{self.name} must be callable, got {self.value_repr}'
                )


    def _assert_type_or_subclass(self):
        self._check_type(value=self.value, name=self.name)


    def _to_effective_list(self, value):
        if value is None:
            return None

        if (
            not self.has_types
            or len(self.types) == 1
            or self.class_mode
            ):
            return value

        items = [
            item for item in value
            if isinstance(item, self.value_type)
            ]

        if not items:
            return None

        lookup = self._try_to_set(items)

        if lookup is None:
            return items

        return lookup


    def _assert_not_blacklisted(self):
        values = self.effective_blacklist

        if values is not None and self.value in values:
            raise ValueError(
                f'{self.name} cannot be in {values}, got: {self.value!r}'
                )


    def _assert_whitelisted(self):
        values = self.effective_whitelist

        if values is not None and self.value not in values:
            raise ValueError(
                f'{self.name} must be in {values}, got: {self.value!r}'
                )


    def _assert_not_empty(self):
        if not self.allow_empty and len(self.value) == 0:
            raise ValueError(
                f'{self.name} cannot be empty.'
                )


    def _assert_stripped(self):
        if (
            self.require_stripped
            and self.is_string
            and self.value != self.value.strip()
            ):
            raise ValueError(
                f'{self.name} must be stripped, got: {self.value!r}'
                )


    def _assert_not_blank(self):
        if (
            not self.allow_blank
            and self.is_string
            and not self.value.strip()
            ):
            raise ValueError(
                f'{self.name} cannot be blank, got: {self.value!r}'
                )


    def _assert_not_whitespace(self):
        if (
            not self.allow_whitespace
            and self.is_string
            and any(char.isspace() for char in self.value)
            ):
            raise ValueError(
                f'{self.name} cannot contain whitespace, got: {self.value!r}'
                )


    def _assert_matches_pattern(self):
        if (
            self.pattern is not None
            and self.is_string
            and not bool(self.pattern.fullmatch(self.value))
            ):
            raise ValueError(
                f'{self.name} does not match the required pattern '
                f'({self.pattern.pattern}), got: {self.value!r}'
                )


    def _assert_finite(self):
        if (
            self.require_finite
            and not np.isfinite(self.value)
            ):
            raise TypeError(
                f'{self.name} must be finite, got: {self.value_repr}.'
                )


    def _raise_bound_error(self, symbol, bound):
        raise ValueError(
            f'{self.name} must be {symbol} {bound}, got: {self.value!r}'
            )


    def _assert_meets_minimum(self):
        if self.min_value is None:
            return

        symbol = None

        if self.min_inclusive:
            if self.value < self.min_value:
                symbol = '≥'
        else:
            if self.value <= self.min_value:
                symbol = '>'

        if symbol is not None:
            self._raise_bound_error(symbol, self.min_value)


    def _assert_meets_maximum(self):
        if self.max_value is None:
            return

        symbol = None

        if self.max_inclusive:
            if self.value > self.max_value:
                symbol = '≤'
        else:
            if self.value >= self.max_value:
                symbol = '<'

        if symbol is not None:
            self._raise_bound_error(symbol, self.max_value)