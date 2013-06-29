from fields import Field
from fields.ListField import ListField

import copy

class SchemaObject(object):

    # Initialize _collections table. This variable maps lower-cased class names
    # to class references.
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
        """ Prepare and retrieve schema fields. """
        # TODO: This checks all class-level fields whenever a new record is
        # instantiated. Is this the expected behavior?
        #
        out = {}
        found_primary = False
        for k,v in self.__class__.__dict__.items():

            if not isinstance(v, Field):
                continue

            # Check for primary key
            if v._is_primary:
                if not found_primary:
                    self._primary_name = k
                    found_primary = True
                else:
                    raise Exception('Multiple keys are not supported')

            # Check for list
            if v._list:
                # Create ListField instance
                # TODO: Should this also pass kwargs? I *think* this setup means that,
                # for example, ListField defaults are never set by the user.
                v = ListField(v)
                # Replace class-level descriptor with ListField
                setattr(self.__class__, k, v)
            out[k] = v

        return out

    def __init__(self, **kwargs):

        # Set _primary_name to '_id' by default
        self._primary_name = '_id'

        # Store dict of class-level Field instances
        self._fields = self._get_fields()

        # Set all instance-level field values to defaults
        for k,v in self._fields.items():
            setattr(self, k, copy.deepcopy(v._default))

        # Add kwargs to instance
        for k,v in kwargs.items():
            setattr(self, k, v)