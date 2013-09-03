import copy

import logging
import warnings

from fields import Field, ListField, ForeignField, ForeignList
from .storage import Storage
from .query import QueryBase, RawQuery
from .frozen import FrozenDict
from .exceptions import ModularOdmException

class ContextLogger(object):

    @staticmethod
    def sort_func(e):
        return (e.xtra._name, e.func.__name__)

    def report(self, sort_func=None):
        return self.logger.report(sort_func or self.sort_func)

    def __init__(self, log_level=None, xtra=None, sort_func=None):
        self.log_level = log_level
        self.xtra = xtra
        self.sort_func = sort_func or self.sort_func
        self.logger = Storage.logger

    def __enter__(self):
        self.listening = self.logger.listen(self.xtra)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.listening:
            report = self.logger.report(
                lambda e: (e.xtra._name, e.func.__name__)
            )
            if self.log_level is not None:
                logging.log(self.log_level, report)
            self.logger.clear()
        self.logger.pop()

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

        cls = this if isinstance(this, type) else type(this)

        with ContextLogger(log_level=this._log_level, xtra=cls):
            return func(this, *args, **kwargs)

    return wrapped

def warn_if_detached(func):
    """ Warn if self / cls is detached. """
    @wraps(func)
    def wrapped(this, *args, **kwargs):
        # Check for _detached in __dict__ instead of using hasattr
        # to avoid infinite loop in __getattr__
        if '_detached' in this.__dict__ and this._detached:
            warnings.warn('here')
        return func(this, *args, **kwargs)
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
        cls._log_level = hasattr(cls, '_meta') and \
            cls._meta.get('log_level', None)

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
    _dirty = {}

    def __init__(self, **kwargs):

        self.__backrefs = {}
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
        if self is other:
            return True
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
    def _storage_key(self):
        """ Primary key passed through translator. """
        return self._pk_to_storage(self._primary_key)

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
            data['__backrefs'] = self.__backrefs

        return data

    @classmethod
    @has_storage
    def from_storage(cls, data, translator=None):

        # result = cls()
        result = {}

        for key, value in data.items():

            field_object = cls._fields.get(key, None)

            if isinstance(field_object, Field):
                data_value = data[key]
                if data_value is None:
                    value = None
                    # setattr(result, key, None)
                    result[key] = None
                else:
                    value = field_object.from_storage(data_value, translator)
                # field_object.__set__(result, value, safe=True)
                result[key] = value

            else:
                # setattr(result, key, value)
                result[key] = value

        # result._is_loaded = False

        return result

    def clone(self):
        return self.load_from_data(
            self.to_storage(clone=True),
            _is_loaded=False
        )

    # Backreferences

    @property
    def _backrefs(self):
        return FrozenDict(**self.__backrefs)

    @_backrefs.setter
    def _backrefs(self, _):
        raise ModularOdmException('Cannot modify backrefs.')

    @property
    def _backrefs_flat(self):
        return flatten_backrefs(self._backrefs)

    def _remove_backref(self, backref_key, parent, parent_field_name):
        self.__backrefs[backref_key][parent._name][parent_field_name].remove(parent._primary_key)
        self.save()

    def _set_backref(self, backref_key, parent_field_name, backref_value):

        backref_value_class_name = backref_value.__class__._name
        backref_value_primary_key = backref_value._primary_key

        if backref_value_primary_key is None:
            raise Exception('backref object\'s primary key must be saved first')

        if backref_key not in self._backrefs:
            self.__backrefs[backref_key] = {}
        if backref_value_class_name not in self._backrefs[backref_key]:
            self.__backrefs[backref_key][backref_value_class_name] = {}
        if parent_field_name not in self._backrefs[backref_key][backref_value_class_name]:
            self.__backrefs[backref_key][backref_value_class_name][parent_field_name] = []

        append_to = self.__backrefs[backref_key][backref_value_class_name][parent_field_name]
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

        for field_name, field_object in self._fields.items():
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
    def _add_dirty(cls, storage_key):
        if cls._name not in cls._dirty:
            cls._dirty[cls._name] = []
        cls._dirty[cls._name].append(storage_key)

    @classmethod
    def _rm_dirty(cls, storage_key):
        if cls._name not in cls._dirty:
            return
        cls._dirty[cls._name].remove(storage_key)

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

        return cls.load_from_data(data, _is_loaded=True)

    @classmethod
    def load_from_data(cls, data, _is_loaded):

        loaded_object = cls()

        loaded_data = cls.from_storage(data)
        for key, value in loaded_data.items():
            if key in loaded_object._fields:
                field_object = loaded_object._fields[key]
                field_object.__set__(loaded_object, value, safe=True)
            else:
                setattr(loaded_object, key, value)

        loaded_object._is_loaded = _is_loaded

        if _is_loaded and loaded_object._primary_key:
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
            self.update_one(self._primary_key, self.to_storage(), saved=True)
        elif self._is_optimistic and self._primary_key is None:
            self._optimistic_insert()
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

    def __getattribute__(self, item):
        cls = object.__getattribute__(self, '__class__')
        if hasattr(cls, '_storage') and cls._storage:
            field_object = cls._fields[cls._primary_name]
            key = field_object.data.get(self)
            storage_key = cls._pk_to_storage(key)
            dirty = cls._name in cls._dirty \
                and storage_key in cls._dirty[cls._name]
            if dirty:
                cls._rm_dirty(storage_key)
                object.__getattribute__(self, 'reload')()
        return object.__getattribute__(self, item)

    def reload(self):

        storage_data = self._storage[0].get(self.__class__, self._storage_key)

        for key, value in storage_data.items():
            field_object = self._fields.get(key, None)
            if isinstance(field_object, Field):
                data_value = storage_data[key]
                if data_value is None:
                    value = None
                    setattr(self, key, None)
                else:
                    value = field_object.from_storage(data_value)
                field_object.__set__(self, value, safe=True)

        self._set_cache(self._storage_key, self)

    @warn_if_detached
    def __getattr__(self, item):
        if item in self._backrefs:
            return self._backrefs[item]
        errmsg = '{cls} object has no attribute {item}'.format(
            self.__class__.__name__,
            item
        )
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
                raise AttributeError(errmsg)
            return ForeignList(ids, base_class=StoredObject.get_collection(parent_schema_name))
        raise AttributeError(errmsg)

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
    def find(cls, *args, **kwargs):
        return cls._storage[0].QuerySet(cls, cls._storage[0].find(*args, **kwargs))

    @classmethod
    @has_storage
    def find_one(cls, *query):
        return cls.load_from_data(cls._storage[0].find_one(*query), _is_loaded=True)

    @classmethod
    @has_storage
    def get(cls, key):
        return cls.load(cls._storage[0].get(cls, cls._pk_to_storage(key)))

    @classmethod
    @has_storage
    def insert(cls, key, val):
        cls._storage[0].insert(cls, cls._pk_to_storage(key), val)

    # @classmethod
    # @has_storage
    # def update(cls, key, data):
    #     cls._storage[0].update(cls, cls._pk_to_storage(key), data)

    @classmethod
    def _prepare_update(cls, data):

        storage_data = {}
        includes_foreign = False

        for key, value in data.items():
            if key in cls._fields:
                field_object = cls._fields[key]
                if field_object._is_foreign and not includes_foreign:
                    includes_foreign = True
                if key == cls._primary_name:
                    continue
                storage_data[key] = field_object.to_storage(value)
            else:
                storage_data[key] = value

        return storage_data, includes_foreign

    def _update_in_memory(self, storage_data):
        for field_name, data_value in storage_data.items():
            field_object = self._fields[field_name]
            field_object.__set__(self, data_value, safe=True)
        self.save()

    @classmethod
    def _which_to_obj(cls, which):
        if isinstance(which, list) and isinstance(which[0], QueryBase):
            return cls.find_one(which)
        if isinstance(which, StoredObject):
            return which
        return cls.load(cls._pk_to_storage(which))

    @classmethod
    @has_storage
    def update_one(cls, which, data, saved=False):

        storage_data, includes_foreign = cls._prepare_update(data)
        obj = cls._which_to_obj(which)

        if saved or not includes_foreign:
            cls._storage[0].update(
                RawQuery(
                    cls._primary_name, 'eq', obj._primary_key
                ),
                storage_data,
            )
            if not saved:
                cls._clear_caches(obj._storage_key)
        else:
            obj._update_in_memory(storage_data)

    @classmethod
    @has_storage
    def update(cls, query, data):

        storage_data, includes_foreign = cls._prepare_update(data)

        objs = cls.find(query)
        keys = objs.get_keys()

        if not includes_foreign:
            cls._storage[0].update(query, storage_data)
            for key in keys:
                cls._add_dirty(key)
                cls._clear_caches(key)

        else:
            for obj in objs:
                obj._update_in_memory(storage_data)

    @classmethod
    @has_storage
    def remove_one(cls, which, rm=True):

        # Look up object
        obj = cls._which_to_obj(which)

        # Remove references
        rm_fwd_refs(obj)
        rm_back_refs(obj)

        # Detach and remove from cache
        obj._detached = True
        cls._clear_caches(obj._storage_key)

        # Remove from backend
        if rm:
            cls._storage[0].remove(
                RawQuery(obj._primary_name, 'eq', obj._storage_key)
            )

    @classmethod
    @has_storage
    def remove(cls, *query):

        objs = cls.find(*query)

        for obj in objs:
            cls.remove_one(obj, rm=False)

        cls._storage[0].remove(*query)

def rm_fwd_refs(obj):
    """ Remove forward references to linked fields. """

    for stack, key in obj._backrefs_flat:

        # Unpack stack
        backref_key, parent_schema_name, parent_field_name = stack

        # Get parent info
        parent_schema = StoredObject._collections[parent_schema_name]
        parent_key_store = parent_schema._pk_to_storage(key)
        parent_object = parent_schema.load(parent_key_store)

        # Remove forward references
        if parent_object._fields[parent_field_name]._list:
            getattr(parent_object, parent_field_name).remove(obj)
        else:
            parent_field_object = parent_object._fields[parent_field_name]
            setattr(parent_object, parent_field_name, parent_field_object._gen_default())

        # Save
        parent_object.save()

def rm_back_refs(obj):
    """ Remove backward references from linked fields. """

    for field_name, field_object in obj._fields.items():

        delete_queue = []

        if isinstance(field_object, ForeignField):
            value = getattr(obj, field_name)
            if value:
                delete_queue.append(value)
            field_instance = field_object

        elif isinstance(field_object, ListField):
            field_instance = field_object._field_instance
            if isinstance(field_instance, ForeignField):
                delete_queue = getattr(obj, field_name)

        else:
            continue

        for obj_to_delete in delete_queue:
            obj_to_delete._remove_backref(
                field_instance._backref_field_name,
                obj,
                field_name,
            )
