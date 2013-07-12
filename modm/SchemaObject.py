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
        for field_name, field_object in self._fields.items():
            # print '***', field_name, getattr(self, field_name)
            if field_name == 'tag':
                # print self.tag._primary_key
                # print [v.value for i,v in self._cache['tag'].items()]
                pass
        dtmp = {field_name:field_object.to_storage(getattr(self, field_name)) for field_name, field_object in self._fields.items()}

        if self._backrefs:
            dtmp['_backrefs'] = self._backrefs
        return dtmp

    def _process_and_get_fields(self):
        """ Prepare and retrieve schema fields. """
        # TODO: This checks all class-level fields whenever a new record is
        # instantiated. Is this the expected behavior?
        #
        out = {}
        found_primary = False
        for k,v in self.__class__.__dict__.items():

            if not isinstance(v, Field):
                continue

            v._parent = self

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
                v = ListField(v) # v is the field that is being list-ified
                # Replace class-level descriptor with ListField
                setattr(self.__class__, k, v)

            out[k] = v

        return out

    def __init__(self, **kwargs):

        self._is_loaded = kwargs.pop('_is_loaded', False)

        # Set _primary_name to '_id' by default
        self._primary_name = '_id'

        # Store dict of class-level Field instances
        self._fields = self._process_and_get_fields()

        # Set all instance-level field values to defaults
        if not self._is_loaded:
            for k,v in self._fields.items():
                setattr(self, k, copy.deepcopy(v._default))

        # Add kwargs to instance
        for k,v in kwargs.items():
            # if isinstance(getattr(self, k), ListField):
            #     print v
            setattr(self, k, v)