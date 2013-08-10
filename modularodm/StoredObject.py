import copy

import logging

from fields import Field
from fields.ListField import ListField
from .storage import Storage

from functools import wraps
def has_storage(func):
    """ Ensure that self/cls contains a Storage backend. """
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        me = args[0]
        if not hasattr(me, '_storage') or \
                not me._storage:
            raise Exception('No storage backend attached to schema <{}>.'.format(
                me._name.upper())
            )
        return func(*args, **kwargs)
    return wrapped_func

class SOMeta(type):

    def __init__(cls, name, bases, dct):

        # Run super-metaclass __init__
        super(SOMeta, cls).__init__(name, bases, dct)

        # Store prettified name
        cls._name = name.lower()

        # Prepare fields
        cls._fields = {}
        cls._primary_name = '_id'

        cls._found_primary = False

        for key, value in cls.__dict__.iteritems():

            # Skip if not descriptor
            if not isinstance(value, Field):
                continue

            # Add field
            cls._add_field(key, value)

        # Must be a primary key
        if cls._fields and not cls._found_primary:
            if '_id' not in cls._fields:
                raise Exception('Schemas must either define a field named _id or specify exactly one field as primary.')

        # Delete temporary attribute
        del cls._found_primary

    @property
    def _translator(cls):
        return cls._storage[0].Translator

class StoredObject(object):

    __metaclass__ = SOMeta

    _collections = {}
    _cache = {} # todo implement this with save and load
    _object_cache = {}

    @classmethod
    def _add_field(cls, field_name, field_obj):

        # Memorize parent references
        field_obj._schema_class = cls
        field_obj._field_name = field_name

        # Check for primary key
        if field_obj._is_primary:
            if not cls._found_primary:
                cls._primary_name = field_name
                cls._found_primary = True
            else:
                raise Exception('Multiple primary keys are not supported.')

        # Wrap in list
        if field_obj._list:
            field_obj = ListField(
                field_obj,
                **field_obj._kwargs
            )
            # Memorize parent references
            field_obj._schema_class = cls
            field_obj._field_name = field_name
            # Set parent pointer of child field to list field
            field_obj._field_instance._list_container = field_obj

        # Store descriptor to cls, cls._fields
        setattr(cls, field_name, field_obj)
        cls._fields[field_name] = field_obj

    def __init__(self, **kwargs):

        self._backrefs = {}
        self._is_loaded = False # this gets passed in via kwargs in self.load
        self._is_optimistic = hasattr(self, '_meta') and self._meta.get('optimistic', False)

        self._is_loaded = kwargs.pop('_is_loaded', False)

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

    def __str__(self):

        return str({field : str(getattr(self, field)) for field in self._fields})

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

    @property
    @has_storage
    def _translator(self):
        return self.__class__._translator

    @has_storage
    def to_storage(self, translator=None):

        data = {}

        for field_name, field_object in self._fields.iteritems():
            field_value = field_object.to_storage(field_object._get_underlying_data(self), translator)
            data[field_name] = field_value

        if self._backrefs:
            data['_backrefs'] = self._backrefs

        return data

    @classmethod
    @has_storage
    def from_storage(cls, data, translator=None):

        result = cls()

        for key, value in data.iteritems():

            field_object = cls._fields.get(key, None)

            if isinstance(field_object, Field):

                data_value = data[key]
                if data_value is None:
                    setattr(result, key, None)
                else:
                    setattr(
                        result,
                        key,
                        field_object.from_storage(data_value, translator)
                    )

            else:

                setattr(result, key, value)

        result._is_loaded = True

        return result

    def __getattribute__(self, name):
        return super(StoredObject, self).__getattribute__(name)

    def _remove_backref(self, backref_field_name, cls, primary_key):
        self._backrefs[backref_field_name][cls._name].remove(primary_key)
        # self.save()
        print repr(self), self._backrefs, self.to_storage()['_backrefs']

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
        if not isinstance(storage, Storage):
            raise Exception('Argument to set_storage must be an instance of Storage.')
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
        trans_key = cls._pk_to_storage(key)
        if cls._name in cls._object_cache and trans_key in cls._object_cache[cls._name]:
            return cls._object_cache[cls._name][trans_key]

    @classmethod
    def _set_cache(cls, key, obj):

        trans_key = cls._pk_to_storage(key)

        if cls._name not in cls._object_cache:
            cls._object_cache[cls._name] = {}

        cls._object_cache[cls._name][trans_key] = obj

        if cls._name not in cls._cache:
            cls._cache[cls._name] = {}
        cls._cache[cls._name][trans_key] = obj.to_storage()

    @classmethod
    def _get_cache(cls, key):
        trans_key = cls._pk_to_storage(key)
        if cls._name in cls._object_cache and trans_key in cls._object_cache[cls._name]:
            return cls._object_cache[cls._name][trans_key].to_storage()
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
            # if current_data[field_name] != cached_data[field_name]:
            # Diff exists current and cached data don't match OR if
            # field not present in cached data; this can happen on
            # dynamic column addition
            if field_name not in cached_data \
                    or current_data[field_name] != cached_data[field_name]:
                field_list.append(field_name)

        return field_list

    ###########################################################################

    @classmethod
    @has_storage
    def load(cls, key):

        # todo rename to get?

        # Try loading from object cache
        cached_object = cls._load_from_cache(key)
        if cached_object is not None:
            return cached_object

        # Try loading from storage cache
        data = copy.deepcopy(cls._storage[0].get(cls, cls._pk_to_storage(key))) # better way to do this? Otherwise on load, the Storage.store
                                                            #  look just like changed object

        # if not found in either cache, return None
        if not data:
            return None

        # Load from storage cache data
        loaded_object = cls.from_storage(data)

        # Add to caches
        cls._set_cache(key, loaded_object)

        return loaded_object

    @classmethod
    def _must_be_loaded(cls, value):
        if value is not None and not value._is_loaded:
            raise Exception('Record must be loaded.')

    @has_storage
    def save(self):

        for field_name, field_object in self._fields.iteritems():
            if hasattr(field_object, 'on_before_save'):
                field_object.on_before_save(self)

        # Validate
        for field_name, field_obj in self._fields.iteritems():
            field_obj.do_validate(getattr(self, field_name))

        if self._primary_key is not None and self._is_cached(self._primary_key):
            list_on_save_after_fields = self._get_list_of_differences_from_cache()
        else:
            list_on_save_after_fields = self._fields.keys()

        if self._is_loaded:
            self.update(self._primary_key, self.to_storage())
        elif self._is_optimistic:
            self._primary_key = self._storage[0].optimistic_insert(self.__class__, self.to_storage()) # do a local update; no dirty
        else:
            self.insert(self._primary_key, self.to_storage())

        # if primary key has changed, follow back references and update
        # AND
        # run after_save or after_save_on_difference

        self._is_loaded = True

        for field_name in list_on_save_after_fields:
            field_object = self._fields[field_name]
            if hasattr(field_object, 'on_after_save'):
                cached_data = self._get_cached_data(self._primary_key)
                if cached_data:
                    cached_data = cached_data.get(field_name, None)
                field_object.on_after_save(self, cached_data, getattr(self, field_name))

        self._set_cache(self._primary_key, self)

        return True # todo raise exception on not save

    def __getattr__(self, item):
        # TODO: on remove, kill empty lists of backrefs
        if item in self._backrefs:
            return self._backrefs[item]
        raise AttributeError(item + ' not found')

    # Querying ######

    @classmethod
    @has_storage
    def _pk_to_storage(cls, key):
        return cls._fields[cls._primary_name].to_storage(key)

    @classmethod
    @has_storage
    def find_all(cls):
        return cls._storage[0].QuerySet(cls, cls._storage[0].find_all())

    @classmethod
    @has_storage
    def find(cls, *args, **kwargs):
        return cls._storage[0].QuerySet(cls, cls._storage[0].find(*args, **kwargs))

    @classmethod
    @has_storage
    def find_one(cls, **kwargs):
        return cls.load(cls._storage[0].find_one(cls, **kwargs))

    @classmethod
    @has_storage
    def get(cls, key):
        return cls.load(cls._storage[0].get(cls, cls._pk_to_storage(key)))

    @classmethod
    @has_storage
    def insert(cls, key, val):
        cls._storage[0].insert(cls, cls._pk_to_storage(key), val)

    @classmethod
    @has_storage
    def update(cls, key, val):
        cls._storage[0].update(cls, cls._pk_to_storage(key), val)

    @classmethod
    @has_storage
    def remove(cls, key):
        cls._storage[0].remove(cls._pk_to_storage(key))