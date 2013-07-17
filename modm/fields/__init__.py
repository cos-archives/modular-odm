#from .ListField import *

import weakref
import collections
import warnings

class List(collections.MutableSequence):
    def __init__(self, value=None, **kwargs):
        if value is not None:
            # todo try..catch this at an appropriate place (e.g., ListField)
            self.data = list(value)
        else:
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
        '''
        This dispatches to the getitem method of list
        '''
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

        self.data = weakref.WeakKeyDictionary()

        self._validate = kwargs.get('validate', False)
        if hasattr(self._validate, '__call__'):
            self.validate = self._validate

        #if not hasattr(self, '_default'):
        self._default = kwargs.get('default', self.default)

        self._is_primary = kwargs.get('primary', False)
        self._is_optimistic = kwargs.get("optimistic", None) # todo required?

        self._list = kwargs.get('list', False)

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

    def on_save(self):
        pass

    def __set__(self, instance, value):
        if self._validate and hasattr(self, 'validate'):
            if not self.validate(value):
                raise Exception('Not validated')
        self.data[instance] = value

    def __get__(self, instance, owner):
        return self.data.get(instance, None)

    def __delete__(self):
        pass