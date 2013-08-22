import copy

import logging
import warnings
import pprint

from fields import Field, ListField, ForeignField, ForeignList
from .storage import Storage

def deref(data, keys, missing=None):
    if keys[0] in data:
        if len(keys) == 1:
            return data[keys[0]]
        return deref(data[keys[0]], keys[1:], missing=missing)
    return missing

def flatten_backrefs(data, stack=None):

    stack = stack or []

    if isinstance(data, list):
        return [(stack, item) for item in data]

    out = []
    for key, val in data.items():
        out.extend(flatten_backrefs(val, stack + [key]))

    return out

from functools import wraps

def log_storage(func):

    @wraps(func)
    def wrapped(this, *args, **kwargs):

        logger = this._storage[0].logger
        listening = logger.listen()

        out = func(this, *args, **kwargs)

        if listening:
            logging.debug(pprint.pprint(logger.report()))
            logger.clear()

        return out

    return wrapped

def warn_if_detached(func):
    """ Warn if self / cls is detached. """
    @wraps(func)
    def wrapped(mcs, *args, **kwargs):
        # Check for _detached in __dict__ instead of using hasattr
        # to avoid infinite loop in __getattr__
        if '_detached' in mcs.__dict__ and mcs._detached:
            warnings.warn('here')
        return func(mcs, *args, **kwargs)
    return wrapped

def has_storage(func):
    """ Ensure that self/cls contains a Storage backend. """
    @wraps(func)
    def wrapped(*args, **kwargs):
        me = args[0]
        if not hasattr(me, '_storage') or \
                not me._storage:
            raise Exception('No storage backend attached to schema <{}>.'.format(
                me._name.upper())
            )
        return func(*args, **kwargs)
    return wrapped

class ObjectMeta(type):

    def __init__(cls, name, bases, dct):

        # Run super-metaclass __init__
        super(ObjectMeta, cls).__init__(name, bases, dct)

        # Store prettified name
        cls._name = name.lower()

        # Store optimism
        cls._is_optimistic = hasattr(cls, '_meta') and \
            cls._meta.get('optimistic', False)

        # Prepare fields
        cls._fields = {}
        cls._primary_name = None
        cls._primary_type = None

        for key, value in cls.__dict__.items():

            # Skip if not descriptor
            if not isinstance(value, Field):
                continue

            # Memorize parent references
            value._schema_class = cls
            value._field_name = key

            # Check for primary key
            if value._is_primary:
                if cls._primary_name is None:
                    cls._primary_name = key
                    cls._primary_type = value.data_type
                else:
                    raise Exception('Multiple primary keys are not supported.')

            # Wrap in list
            if value._list:
                value = ListField(
                    value,
                    **value._kwargs
                )
                # Memorize parent references
                value._schema_class = cls
                value._field_name = key
                # Set parent pointer of child field to list field
                value._field_instance._list_container = value

            # Store descriptor to cls, cls._fields
            setattr(cls, key, value)
            cls._fields[key] = value

        # Must have a primary key
        if cls._fields:
            if cls._primary_name is None:
                if '_id' in cls._fields:
                    primary_field = cls._fields['_id']
                    primary_field._primary = True
                    if 'index' not in primary_field._kwargs or not primary_field._kwargs['index']:
                        primary_field._index = True
                    cls._primary_name = '_id'
                    cls._primary_type = cls._fields['_id'].data_type
                else:
                    raise Exception('Schemas must either define a field named _id or specify exactly one field as primary.')

        # Register
        cls.register_collection()

    @property
    def _translator(cls):
        return cls._storage[0].translator

class StoredObject(object):

    __metaclass__ = ObjectMeta

    _collections = {}
    _cache = {}
    _object_cache = {}

    def __init__(self, **kwargs):

        self._backrefs = {}
        self._detached = False
        self._is_loaded = kwargs.pop('_is_loaded', False)

        # Set all instance-level field values to defaults
        if not self._is_loaded:
            for field_name, field_object in self._fields.items():
                field_object.__set__(self, field_object._gen_default(), safe=True)

        # Add kwargs to instance
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self, other):
        return self.to_storage() == other.to_storage()

    @warn_if_detached
    def __unicode__(self):
        return unicode({field : unicode(getattr(self, field)) for field in self._fields})

    @warn_if_detached
    def __str__(self):
        return unicode(self).decode('ascii', 'replace')

    @classmethod
    def register_collection(cls):
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
    def to_storage(self, translator=None, clone=False):

        data = {}

        for field_name, field_object in self._fields.items():
            if clone and field_object._is_primary:
                continue
            field_value = field_object.to_storage(
                field_object._get_underlying_data(self),
                translator
            )
            data[field_name] = field_value

        if not clone and self._backrefs:
            data['_backrefs'] = self._backrefs

        return data

    @classmethod
    @has_storage
    def from_storage(cls, data, translator=None):

        result = cls()

        for key, value in data.items():

            field_object = cls._fields.get(key, None)

            if isinstance(field_object, Field):
                data_value = data[key]
                if data_value is None:
                    value = None
                    setattr(result, key, None)
                else:
                    value = field_object.from_storage(data_value, translator)
                field_object.__set__(result, value, safe=True)

            else:
                setattr(result, key, value)

        result._is_loaded = True

        return result

    def clone(self):
        return self.from_storage(self.to_storage(clone=True))

    # Backreferences

    @property
    def _backrefs_flat(self):
        return flatten_backrefs(self._backrefs)

    def _remove_backref(self, backref_key, parent, parent_field_name):
        self._backrefs[backref_key][parent._name][parent_field_name].remove(parent._primary_key)

    def _set_backref(self, backref_key, parent_field_name, backref_value):

        backref_value_class_name = backref_value.__class__._name
        backref_value_primary_key = backref_value._primary_key

        if backref_value_primary_key is None:
            raise Exception('backref object\'s primary key must be saved first')

        if backref_key not in self._backrefs:
            self._backrefs[backref_key] = {}
        if backref_value_class_name not in self._backrefs[backref_key]:
            self._backrefs[backref_key][backref_value_class_name] = {}
        if parent_field_name not in self._backrefs[backref_key][backref_value_class_name]:
            self._backrefs[backref_key][backref_value_class_name][parent_field_name] = []

        append_to = self._backrefs[backref_key][backref_value_class_name][parent_field_name]
        if backref_value_primary_key not in append_to:
            append_to.append(backref_value_primary_key)

        self.save()

    @classmethod
    def set_storage(cls, storage):

        if not isinstance(storage, Storage):
            raise Exception('Argument to set_storage must be an instance of Storage.')
        if not hasattr(cls, '_storage'):
            cls._storage = []

        for field_name, field_object in cls._fields.items():
            if field_object._index:
                storage._ensure_index(field_name)

        cls._storage.append(storage)

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

    # Cache clearing

    @classmethod
    def _clear_data_cache(cls, key=None):
        if cls is StoredObject:
            cls._cache = {}
        if key is not None:
            cls._cache[cls._name].pop(key, None)
        else:
            cls._cache[cls._name] = {}

    @classmethod
    def _clear_object_cache(cls, key=None):
        if cls is StoredObject:
            cls._object_cache = {}
        if key is not None:
            cls._object_cache[cls._name].pop(key, None)
        else:
            cls._object_cache[cls._name] = {}

    @classmethod
    def _clear_caches(cls, key=None):
        cls._clear_data_cache(key)
        cls._clear_object_cache(key)

    ###########################################################################

    @classmethod
    def _to_primary_key(cls, value):

        if value is None:
            return value

        if isinstance(value, cls):
            return value._primary_key

        return cls._check_pk_type(value)

    @classmethod
    def _check_pk_type(cls, key):

        if isinstance(key, cls._primary_type):
            return key

        try:
            cls._primary_type()
            cast_type = cls._primary_type
        except:
            cast_type = str

        try:
            key = cast_type(key)
        except:
            raise Exception(
                'Invalid key type: {key}, {type}, {ptype}.'.format(
                    key=key, type=type(key), ptype=cast_type
                )
            )

        return key


    @classmethod
    @has_storage
    @log_storage
    def load(cls, key):

        key = cls._check_pk_type(key)

        # Try loading from object cache
        cached_object = cls._load_from_cache(key)
        if cached_object is not None:
            return cached_object

        # Try loading from backend
        data = copy.deepcopy(cls._storage[0].get(cls, cls._pk_to_storage(key)))

        # if not found, return None
        if not data:
            return None

        # Load from backend data
        loaded_object = cls.from_storage(data)

        # Add to cache
        cls._set_cache(loaded_object._primary_key, loaded_object)

        return loaded_object

    @classmethod
    def _must_be_loaded(cls, value):
        if value is not None and not value._is_loaded:
            raise Exception('Record must be loaded.')

    @has_storage
    @log_storage
    def _optimistic_insert(self):
        self._primary_key = self._storage[0]._optimistic_insert(
            self.__class__,
            self.to_storage()
        )

    @has_storage
    @log_storage
    def save(self):

        if self._detached:
            raise Exception('Cannot save detached object.')

        for field_name, field_object in self._fields.items():
            if hasattr(field_object, 'on_before_save'):
                field_object.on_before_save(self)

        if self._primary_key is not None and self._is_cached(self._primary_key):
            list_on_save_after_fields = self._get_list_of_differences_from_cache()
        else:
            list_on_save_after_fields = self._fields.keys()

        # Validate
        # for field_name, field_object in self._fields.items():
        # todo: TEST THIS!
        # todo: only save modified fields?
        for field_name in list_on_save_after_fields:
            field_object = self._fields[field_name]
            field_object.do_validate(getattr(self, field_name))

        if self._is_loaded:
            self.update(self._primary_key, self.to_storage())
        elif self._is_optimistic:
            self._optimistic_insert()
            # self._primary_key = self._storage[0]._optimistic_insert(self.__class__, self.to_storage()) # do a local update; no dirty
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
                field_object.on_after_save(self, field_name, cached_data, getattr(self, field_name))

        self._set_cache(self._primary_key, self)

        return True # todo raise exception on not save

    @warn_if_detached
    def __getattr__(self, item):
        # TODO: on remove, kill empty lists of backrefs
        if item in self._backrefs:
            return self._backrefs[item]
        if '__' in item:
            item_split = item.split('__')
            if len(item_split) == 2:
                parent_schema_name, backref_key = item_split
                backrefs = deref(self._backrefs, [backref_key, parent_schema_name], missing={})
                ids = sum(
                    backrefs.values(),
                    []
                )
            elif len(item_split) == 3:
                parent_schema_name, backref_key, parent_field_name = item_split
                ids = deref(self._backrefs, [backref_key, parent_schema_name, parent_field_name], missing=[])
            else:
                raise Exception('uh oh')
            return ForeignList(ids, base_class=StoredObject.get_collection(parent_schema_name))
        raise AttributeError(item + ' not found')

    @warn_if_detached
    def __setattr__(self, key, value):
        if key not in self._fields and not key.startswith('_'):
            warnings.warn('Setting an attribute that is neither a field nor a protected value.')
        super(StoredObject, self).__setattr__(key, value)
        
    # Querying ######

    @classmethod
    def _parse_key_value(cls, value):
        if isinstance(value, StoredObject):
            return value._primary_key, value
        return value, cls.load(cls._pk_to_storage(value))

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
    def find_one(cls, *query):
        return cls.from_storage(cls._storage[0].find_one(*query))

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
    def remove(cls, value):

        key, value = cls._parse_key_value(value)
        key_store = cls._pk_to_storage(key)

        # Remove backrefs from linked fields
        for field_name, field_object in cls._fields.items():

            to_deletes = []

            if isinstance(field_object, ForeignField):
                to_deletes = [getattr(value, field_name)]
                field_instance = field_object
            elif isinstance(field_object, ListField):
                field_instance = field_object._field_instance
                if isinstance(field_instance, ForeignField):
                    to_deletes = getattr(value, field_name)

            for to_delete in to_deletes:
                to_delete._remove_backref(
                    field_instance._backref_field_name,
                    value,
                    field_name,
                )

        # Remove backrefs to linked fields
        for stack, key in value._backrefs_flat:

            # Unpack stack
            backref_key, parent_schema_name, parent_field_name = stack

            # Get parent info
            parent_schema = StoredObject._collections[parent_schema_name]
            parent_key_store = parent_schema._pk_to_storage(key)
            parent_object = parent_schema.load(parent_key_store)

            # Remove backrefs
            if parent_object._fields[parent_field_name]._list:
                getattr(parent_object, parent_field_name).remove(value)
            else:
                parent_field_object = parent_object._fields[parent_field_name]
                setattr(parent_object, parent_field_name, parent_field_object._gen_default())

            parent_object.save()

        # Detach record
        value._detached = True

        # Remove record from cache and database
        cls._clear_caches(key_store)
        cls._storage[0].remove(key_store)
