import copy

import logging

from SchemaObject import SchemaObject
from fields import Field

class StoredObject(SchemaObject):

    _cache = {} # todo implement this with save and load
    _object_cache = {}

    def __init__(self, **kwargs):
        self._backrefs = {}
        self._is_loaded = False # this gets passed in via kwargs in self.load
        self._is_optimistic = self._meta.get('optimistic') if hasattr(self, '_meta') else None
        super(StoredObject, self).__init__(**kwargs)

    def _set_backref(self, backref_key, backref_value):
        backref_value_class_name = backref_value.__class__.__name__.lower() # todo standardized class name getter
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
        cls.register()

    # Caching ################################################################

    @classmethod
    def _is_cached(cls, key):
        class_name = cls.__name__.lower()
        if class_name in cls._cache:
            if key in cls._cache[class_name]:
                return True
        return False

    @classmethod
    def _load_from_cache(cls, key):
        # class_name = cls.__name__.lower()
        # if class_name in cls._object_cache and key in cls._object_cache[class_name]:
        #     return cls._object_cache[class_name][key]

        cached = cls._get_cache(key)
        if cached is None:
            return None
        return cls.load_from_data(cached)

    @classmethod
    def _set_cache(cls, key, obj):
        class_name = cls.__name__.lower()
        # if class_name not in cls._object_cache:
        #     cls._object_cache[class_name] = {}
        # cls._object_cache[class_name][key] = obj

        if class_name not in cls._cache:
            cls._cache[class_name] = {}
        cls._cache[class_name][key] = obj.to_storage()

    @classmethod
    def _get_cache(cls, key):
        class_name = cls.__name__.lower()
        if cls._is_cached(key):
            return cls._cache[class_name][key]
        return None

    def _get_list_of_differences_from_cache(self):

        field_list = []

        if not self._is_loaded:
            return field_list

        logging.debug('Before loading from cache')
        cached_data = self._get_cache(self._primary_key)
        logging.debug('After loading from cache')

        if cached_data == None:
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

    def _copy(self):
        """Deep copy self, including descriptor values. Note: normal deep copy
        won't work with descriptors values, since this won't add replace the
        object in the weak key dictionary.

        It may be better to start with a new instantiation of self.__class__
        and deep copy everything in self.__class__.__dict__.iteritems

        """
        # Captures all non-descriptor values
        copied = copy.deepcopy(self)

        # Copy values of all descriptors
        for key, val in self.__class__.__dict__.iteritems():
            if isinstance(val, Field):
                setattr(copied, key, val.to_storage(getattr(self, key)))
        return copied

    def save(self):
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

        for field_names in list_on_save_after_fields:
            field = self.__class__.__dict__[field_names]
            if hasattr(field, 'on_after_save'):
                field.on_after_save(self)

        self._set_cache(self._primary_key, self)

        return True # todo raise exception on not save

    def __getattr__(self, item):
        if item in self._backrefs:
            return self._backrefs[item]
        raise AttributeError(item + ' not found')

    def __getattribute__(self, name):
        return super(StoredObject, self).__getattribute__(name)