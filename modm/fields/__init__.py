#from .ListField import *

import copy
import weakref

class Field(object):

    default = None

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

        self.data = weakref.WeakKeyDictionary()

        self._validate = kwargs.get('validate', False)
        if hasattr(self._validate, '__call__'):
            self.validate = self._validate
            self._validate = True

        #if not hasattr(self, '_default'):
        self._default = kwargs.get('default', self.default)
        self._list = kwargs.get('list', False)
        self._is_primary = kwargs.get('primary', False)
        self._is_optimistic = kwargs.get("optimistic", None)

    def __set__(self, instance, value):
        if self._validate and hasattr(self, 'validate'):
            if not self.validate(value):
                raise Exception('Not validated')
        self.data[instance] = value

    def __get__(self, instance, owner):
        # if not instance in self.data:
            # todo probably good to check for mutability here
            # self.data[instance] = copy.deepcopy(self._default)
        return self.data.get(instance)

    def __delete__(self):
        pass