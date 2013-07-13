import copy

import logging

from SchemaObject import SchemaObject
from fields import Field

class StoredObject(SchemaObject):

    _cache = {} # todo implement this with save and load

    def __init__(self, **kwargs):
        self._dirty = []
        self._backrefs = {}
        self._is_loaded = False # this gets passed in via kwargs in self.load
        self._is_optimistic = self._meta.get('optimistic') if hasattr(self, '_meta') else None
        super(StoredObject, self).__init__(**kwargs)

    def resolve_dirty(self):
        while self._dirty:
            i = self._dirty.pop()
            if i[0] == 'backref':
                kwargs = i[1]
                object_with_backref = kwargs['object_with_backref']
                backref_key = kwargs['backref_key']
                backref_value_class_name = self.__class__.__name__.lower()
                backref_value_primary_key = self._primary_key
                object_with_backref._set_backref(backref_key, backref_value_class_name, backref_value_primary_key)

    def _set_backref(self, backref_key, backref_value_class_name, backref_value_primary_key):
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
        logging.debug('Loading {key} from cache'.format(key=key))
        class_name = cls.__name__.lower()
        if cls._is_cached(key):
            # todo make the deepcopy an option
            return cls._cache[class_name][key]._copy()
        return None

    @classmethod
    def _set_cache(cls, key, obj):
        class_name = cls.__name__.lower()
        if class_name not in cls._cache:
            cls._cache[class_name] = {}
        cls._cache[class_name][key] = obj._copy()  # copy.deepcopy(obj)

    def _get_list_of_differences_from_cache(self):

        field_list = []

        if not self._is_loaded:
            return field_list

        logging.debug('Before loading from cache')
        cached_object = self._load_from_cache(self._primary_key)
        logging.debug('After loading from cache')

        if cached_object == None:
            return field_list

        for field_name in self._fields:
            import pdb; pdb.set_trace()
            if getattr(self, field_name) != getattr(cached_object, field_name):
                field_list.append(field_name)

        return field_list

    ###########################################################################

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
        logging.debug('_copying ' + str(self.__class__.__name__))
        copied = copy.deepcopy(self)

        # Copy values of all descriptors
        for key, val in self.__class__.__dict__.iteritems():
            if isinstance(val, Field):
                setattr(copied, key, val.to_storage(getattr(self, key)))
        return copied

    def save(self):
        if self._primary_key is not None and self._is_cached(self._primary_key):
            # do diff
            pass

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

        self._set_cache(self._primary_key, self)
        # self.resolve_dirty()

        return True # todo raise exception on not save

    def __getattr__(self, item):
        if item in self._backrefs:
            return self._backrefs[item]
        raise AttributeError(item + ' not found')

    def __getattribute__(self, name):
        return super(StoredObject, self).__getattribute__(name)