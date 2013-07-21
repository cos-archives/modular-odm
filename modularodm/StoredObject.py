import copy

import logging

from fields import Field
from fields.ListField import ListField

class SOMeta(type):

    def __init__(cls, name, bases, dct):

        super(SOMeta, cls).__init__(name, bases, dct)
        cls._name = name.lower()

class StoredObject(object):

    __metaclass__ = SOMeta

    _collections = {}
    _cache = {} # todo implement this with save and load
    _object_cache = {}

    def __init__(self, **kwargs):

        self._backrefs = {}
        self._is_loaded = False # this gets passed in via kwargs in self.load
        self._is_optimistic = hasattr(self, '_meta') and self._meta.get('optimistic', False)

        self._is_loaded = kwargs.pop('_is_loaded', False)

        # Set _primary_name to '_id' by default
        self._primary_name = '_id'

        # Store dict of class-level Field instances
        self._fields = self._process_and_get_fields()

        # Set all instance-level field values to defaults
        if not self._is_loaded:
            for k, v in self._fields.items():
                if hasattr(v._default, '__call__'):
                    setattr(self, k, v._default())
                else:
                    setattr(self, k, copy.deepcopy(v._default))

        # Add kwargs to instance
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def register_collection(cls, **kwargs):
        cls._collections[cls._name] = cls

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
        dtmp = {field_name:field_object.to_storage(field_object.get_underlying_data(self)) for field_name, field_object in self._fields.items()}
        if self._backrefs:
            dtmp['_backrefs'] = self._backrefs
        return dtmp

    def _process_and_get_fields(self):
        """ Prepare and retrieve schema fields. """

        out = {}
        found_primary = False
        for k, v in self.__class__.__dict__.iteritems():

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

            if v._list:
                v = ListField(v)
                setattr(self.__class__, k, v)

            out[k] = v

        return out

    def __getattribute__(self, name):
        return super(StoredObject, self).__getattribute__(name)

    def _remove_backref(self, backref_field_name, cls, primary_key):
        self._backrefs[backref_field_name][cls._name].remove(primary_key)

    def _set_backref(self, backref_key, backref_value):
        backref_value_class_name = backref_value.__class__._name
        backref_value_primary_key = backref_value._primary_key

        if backref_value_primary_key is None:
            raise Exception('backref object\'s primary key must be saved first')

        if backref_key not in self._backrefs:
            self._backrefs[backref_key] = {}
        if backref_value_class_name not in self._backrefs[backref_key]:
            self._backrefs[backref_key][backref_value_class_name] = []
        self._backrefs[backref_key][backref_value_class_name].append(backref_value_primary_key)
        self.save()

    @classmethod
    def set_storage(cls, storage):
        if not hasattr(cls, '_storage'):
            cls._storage = []
        cls._storage.append(storage)
        cls.register_collection()

    # Caching ################################################################

    @classmethod
    def _is_cached(cls, key):
        if cls._name in cls._object_cache:
            if key in cls._object_cache[cls._name]:
                return True
        return False

    @classmethod
    def _load_from_cache(cls, key):
        if cls._name in cls._object_cache and key in cls._object_cache[cls._name]:
            return cls._object_cache[cls._name][key]

        # cached = cls._get_cache(key)
        # if cached is None:
        #     return None
        # return cls.load_from_data(cached)

    @classmethod
    def _set_cache(cls, key, obj):
        if cls._name not in cls._object_cache:
            cls._object_cache[cls._name] = {}
        cls._object_cache[cls._name][key] = obj

        if cls._name not in cls._cache:
            cls._cache[cls._name] = {}
        cls._cache[cls._name][key] = obj.to_storage()

    @classmethod
    def _get_cache(cls, key):
        if cls._name in cls._object_cache and key in cls._object_cache[cls._name]:
            return cls._object_cache[cls._name][key].to_storage()
        # if cls._is_cached(key):
        #     return cls._cache[class_name][key]
        return None

    @classmethod
    def _get_cached_data(cls, key):
        # todo once object cache is renamed we may need to fiddle with _is_cahed and others
        if cls._is_cached(key):
            return cls._cache[cls._name][key]
        return None

    def _get_list_of_differences_from_cache(self):

        field_list = []

        if not self._is_loaded:
            return field_list

        cached_data = self._cache[self.__class__._name][self._primary_key]

        if cached_data is None:
            return field_list

        current_data = self.to_storage()

        for field_name in self._fields:
            if current_data[field_name] != cached_data[field_name]:
                field_list.append(field_name)

        return field_list

    ###########################################################################

    @classmethod
    def load_from_data(cls, data):
        data['_is_loaded'] = True
        return cls(**data)

    @classmethod
    def load(cls, key):
        cached_object = cls._load_from_cache(key)

        if cached_object is not None:
            return cached_object

        data = copy.deepcopy(cls._storage[0].get(key)) # better way to do this? Otherwise on load, the Storage.store
                                                       #  look just like changed object
        if not data:
            return None

        data['_is_loaded'] = True
        loaded_object = cls(**data)

        cls._set_cache(cls, key, loaded_object)
        return loaded_object

    @classmethod
    def _get_descriptor(cls, field_name):
        return cls.__dict__[field_name]

    @classmethod
    def _must_be_loaded(cls, value):
        if value is not None and not value._is_loaded:
            raise Exception('Record must be loaded')

    def save(self):

        for field_name in self._fields:
            field = self._get_descriptor(field_name)
            if hasattr(field, 'on_before_save'):
                field.on_before_save(self)

        if self._primary_key is not None and self._is_cached(self._primary_key):
            list_on_save_after_fields = self._get_list_of_differences_from_cache()
        else:
            list_on_save_after_fields = self._fields.keys()

        if self._is_loaded:
            self._storage[0].update(self._primary_key, self.to_storage())
        elif self._is_optimistic:
            self._primary_key = self._storage[0].optimistic_insert(self.to_storage(), self._primary_name) # do a local update; no dirty
        else:
            self._storage[0].insert(self._primary_key, self.to_storage())

        # if primary key has changed, follow back refrences and update
        # AND
        # run after_save or after_save_on_difference

        self._is_loaded = True

        for field_name in list_on_save_after_fields:
            field = self._get_descriptor(field_name)
            if hasattr(field, 'on_after_save'):
                cached_data = self._get_cached_data(self._primary_key)
                if cached_data:
                    cached_data = cached_data.get(field_name, None)
                field.on_after_save(cached_data, getattr(self, field_name))

        self._set_cache(self._primary_key, self)

        return True # todo raise exception on not save

    def __getattr__(self, item):
        # TODO: on remove, kill empty lists of backrefs
        if item in self._backrefs:
            return self._backrefs[item]
        raise AttributeError(item + ' not found')

    # Querying ######

    @classmethod
    def find_all(cls):
        return cls._storage[0].find_all()

    @classmethod
    def find(cls, **kwargs):
        return cls._storage[0].find(**kwargs)

    @classmethod
    def get(cls, key):
        return cls._storage[0].get(key)

    @classmethod
    def find_one(cls, **kwargs):
        return cls._storage[0].find_one(**kwargs)

    @classmethod
    def get(cls, key):
        return cls._storage[0].get(key)