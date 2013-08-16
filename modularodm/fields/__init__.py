import weakref
import collections
import warnings
import copy

import logging

class List(collections.MutableSequence):

    def __init__(self, value=None, **kwargs):

        self._field_instance = kwargs.get('field_instance', None)

        self.data = []
        if value is None:
            return

        if not hasattr(value, '__iter__'):
            raise Exception(
                'Value to be assigned to list must be iterable; received <{0}>'.format(
                    repr(value)
                )
            )

        for item in value:
            self.append(item)

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        '''
        This dispatches to the getitem method of list
        '''
        return self.data[key]

    def insert(self, index, value):
        self.data.insert(index, value)

    def append(self, value):
        self.data.append(value)

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return '<MutableSequence: '+self.data.__repr__()+'>'

class Field(object):

    default = None
    _list_class = List

    def _prepare_validators(self, _validate):

        if hasattr(_validate, '__iter__'):

            # List of callable validators
            validate = []
            for validator in _validate:
                if hasattr(validator, '__call__'):
                    validate.append(validator)
                else:
                    raise Exception('Validator lists must be lists of callables.')

        elif hasattr(_validate, '__call__'):

            # Single callable validator
            validate = _validate

        elif type(_validate) == bool:

            # Boolean validator
            validate = _validate

        else:

            # Invalid validator type
            raise Exception('Validators must be callables, lists of callables, or booleans.')

        return _validate, validate

    def __init__(self, *args, **kwargs):

        self._args = args
        self._kwargs = kwargs

        # Pointer to containing ListField
        # Set in StoredObject.SOMeta
        self._list_container = None

        self.data = weakref.WeakKeyDictionary()

        self._validate, self.validate = \
            self._prepare_validators(kwargs.get('validate', False))

        self._default = kwargs.get('default', self.default)
        self._is_primary = kwargs.get('primary', False)
        self._list = kwargs.get('list', False)
        self._required = kwargs.get('required', False)
        self._editable = kwargs.get('editable', True)
        self._index = kwargs.get('index', self._is_primary)

    def do_validate(self, value):

        # Check if required
        if value is None:
            if hasattr(self, '_required') and self._required:
                raise Exception('Value <{}> is required.'.format(self._field_name))
            return True

        # Field-level validation
        cls = self.__class__
        if hasattr(cls, 'validate') and \
                self.validate != False:
            cls.validate(value)

        # Schema-level validation
        if self._validate and hasattr(self, 'validate'):
            if hasattr(self.validate, '__iter__'):
                for validator in self.validate:
                    validator(value)
            elif hasattr(self.validate, '__call__'):
                self.validate(value)

        # Success
        return True

    def _gen_default(self):
        if callable(self._default):
            return self._default()
        return copy.deepcopy(self._default)

    def _access_storage(self, direction, value, translator):

        method_name = '%s_%s' % (direction, self.data_type.__name__)

        if hasattr(translator, method_name):
            method = getattr(translator, method_name)
        else:
            method = getattr(translator, '%s_default' % (direction))

        return method(value)

    def to_storage(self, value, translator=None):

        translator = translator or self._schema_class._translator()

        if value is None:
            return translator.null_value

        return self._access_storage('to', value, translator)

    def from_storage(self, value, translator=None):

        translator = translator or self._schema_class._translator()

        if value == translator.null_value:
            return None

        return self._access_storage('from', value, translator)

    def __set__(self, instance, value):
        if not self._editable:
            raise Exception('Field cannot be edited.')
        if instance._detached:
            warnings.warn('Accessing a detached record.')
        self.data[instance] = value

    def __safe_set__(self, instance, value):
        self.data[instance] = value

    def __get__(self, instance, owner):
        if instance._detached:
            warnings.warn('Accessing a detached record.')
        return self.data.get(instance, None)

    def _get_underlying_data(self, instance):
        """Return data from raw data store, rather than overridden
        __get__ methods. Should NOT be overwritten.
        """
        return self.data.get(instance, None)

    def __delete__(self, instance):
        self.data.pop(instance, None)
