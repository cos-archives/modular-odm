import weakref
import collections
import warnings

import logging

class List(collections.MutableSequence):

    def __init__(self, value=None, **kwargs):

        self._field_instance = kwargs.get('field_instance', None)

        self.data = []
        if value is None:
            return

        # todo: where should this exception be raised
        if not hasattr(value, '__iter__'):
            raise Exception(
                'Value to be assigned to list must be iterable; received <{0}>'.format(
                    repr(value)
                )
            )

        for item in value:
            self.append(item)
        self.data = list(value)

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def __setitem__(self, key, value):
        self._field_instance.do_validate(value)
        self.data[key] = value

    def __getitem__(self, key):
        '''
        This dispatches to the getitem method of list
        '''
        return self.data[key]

    def insert(self, index, value):
        self._field_instance.do_validate(value)
        self.data.insert(index, value)

    def append(self, value):
        self._field_instance.do_validate(value)
        self.data.append(value)

    def __repr__(self):
        return '<MutableSequence: '+self.data.__repr__()+'>'

class Field(object):

    default = None
    _list_class = List

    def __init__(self, *args, **kwargs):

        self._args = args
        self._kwargs = kwargs

        self._parent = None # gets set in StoredObject

        self.data = weakref.WeakKeyDictionary()

        # todo:
        self._validate = kwargs.get('validate', False)
        if hasattr(self._validate, '__iter__'):
            self.validate = []
            for validator in self._validate:
                if hasattr(validator, '__call__'):
                    self.validate.append(validator)
        elif hasattr(self._validate, '__call__'):
            self.validate = self._validate

        self._default = kwargs.get('default', self.default)

        self._is_primary = kwargs.get('primary', False)

        self._list = kwargs.get('list', False)

    def do_validate(self, value):
        if self._validate and hasattr(self, 'validate'):
            if hasattr(self.validate, '__iter__'):
                for validator in self.validate:
                    validator(value)
            else:
                self.validate(value)
        return True

    def to_storage(self, value):
        return value

    def on_save(self):
        pass

    def __set__(self, instance, value):
        self.do_validate(value)
        self.data[instance] = value

    def __get__(self, instance, owner=None):
        return self.data.get(instance, None)

    get_underlying_data = __get__

    def __delete__(self):
        pass