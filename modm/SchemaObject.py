from fields import Field
from fields.ListField import ListField

import copy

class SchemaObject(object):
    _collections = {}

    @classmethod
    def register(cls, **kwargs):
        cls._collections[cls.__name__.lower()] = cls

    @classmethod
    def get_collection(cls, name):
        return cls._collections[name.lower()]

    @property
    def _primary_key(self):
        return getattr(self, self._primary_name)

    @_primary_key.setter
    def _primary_key(self, value):
        setattr(self, self._primary_name, value)

    def to_storage(self):
        d = {k:cls.to_storage(getattr(self, k)) for k,cls in self._fields.items()}
        d['_backrefs'] = self._backrefs
        return d

    def _get_fields(self):
        out = {}
        found_primary = False
        for k,v in self.__class__.__dict__.items():
            if isinstance(v, Field):
                if v._is_primary:
                    if not found_primary:
                        self._primary_name = k
                        found_primary = True
                    else:
                        raise Exception('Multiple keys are not supported')

                if v._list:
                    v = ListField(v)
                    setattr(self.__class__, k, v)
                out[k] = v
        return out

    def __init__(self, **kwargs):
        self._primary_name = '_id'
        self._fields = self._get_fields()

        for k,v in self._fields.items():
            setattr(self, k, copy.deepcopy(v._default))

        for k,v in kwargs.items():
            setattr(self, k, v)