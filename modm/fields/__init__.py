#from .ListField import *

import weakref
import collections
import warnings

class List(collections.MutableSequence):
    def __init__(self, *args, **kwargs):
        self.data = []
        self._field_instance = kwargs.get('field_instance', None)

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def __setitem__(self, key, value):
        if self._field_instance.do_validate(value):
            self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def insert(self, index, value):
        if self._field_instance.do_validate(value): # will never return False
            self.data.insert(index, value)

    def append(self, value):
        if self._field_instance.do_validate(value):
            self.data.append(value)

    def __repr__(self):
        return '<MutableSequence: '+self.data.__repr__()+'>'

class Field(object):

    default = None
    _list_class = List

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

        self._parent = None # gets set in SchemaObject

        self.modified_data = weakref.WeakKeyDictionary()
        self.original_data = weakref.WeakKeyDictionary()

        self._validate = kwargs.get('validate', False)
        if hasattr(self._validate, '__call__'):
            self.validate = self._validate

        #if not hasattr(self, '_default'):
        self._default = kwargs.get('default', self.default)

        self._is_primary = kwargs.get('primary', False)
        self._is_optimistic = kwargs.get("optimistic", None) # todo required?

        self._list = kwargs.get('list', False)

    def diff(self, original, modified):
        # is different?
        return not original == modified

    def do_diff(self, instance):
        if instance not in self.original_data:
            return True
        return self.diff(self.original_data[instance], self.modified_data[instance])

    def get_original(self, instance):
        return self.original_data[instance]

    def set_original(self, instance, value):
        self.original_data[instance] = value

    def get_modified(self, instance):
        return self.modified_data[instance]

    # __set__ is set_modified

    def do_validate(self, value):
        if self._validate:
            if not hasattr(self, 'validate'):
                msg = "Can't validate without validate function"
                raise AttributeError(msg)
            if not self.validate(value):
                msg = '{value} did not validate'.format(value=value)
                raise ValueError(msg)
        return True

    def to_storage(self, value):
        return value

    def __set__(self, instance, value):
        if self._validate and hasattr(self, 'validate'):
            if not self.validate(value):
                raise Exception('Not validated')
        self.modified_data[instance] = value

    def __get__(self, instance, owner):
        if instance not in self.modified_data:
            return self.original_data[instance]
        return self.modified_data[instance]

    def __delete__(self):
        pass