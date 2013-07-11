from ..fields import Field, List
from modm.SchemaObject import SchemaObject

import weakref

class ForeignList(List):

    # todo take out caching here

    def __init__(self, *args, **kwargs):
        super(ForeignList, self).__init__(*args, **kwargs)
        self.object_cache = {}

    def as_primary_keys(self):
        out = []
        for i in self.data:
            if isinstance(i, SchemaObject):
                out.append(i._primary_key)
            else:
                out.append(i)
        return out

    def set_cache_object(self, key, value):
        self.object_cache[key] = value

    def get_cache_object(self, key):
        if key in self.object_cache:
            return self.object_cache[key]
        else:
            # todo try this and catch error
            obj = self._field_instance.base_class.load(key)
            self.set_cache_object(key, obj)
            return obj

    def __contains__(self, item):
        # todo needs to be tested
        if isinstance(item, str): # assume item is a primary key
            return item in self.as_primary_keys()
        elif isinstance(item, SchemaObject): # should do an object level comparison rather than
            return item._primary_key in self.as_primary_keys()
        else:
            return False

    def __delitem__(self, key):
        del self.data[key]

    def __setitem__(self, key, value):
        if self._field_instance.do_validate(value):
            super(ForeignList, self).__setitem__(key, value)

    def __getitem__(self, item):
        result = super(ForeignList, self).__getitem__(item) # we're really just dealing with self[item]
        if isinstance(result, list):
            return [self.get_cache_object(i) for i in result]
        return self.get_cache_object(result)

    def insert(self, index, value):
        if self._field_instance.do_validate(value): # will never return False
            super(ForeignList, self).insert(index, value)

    def append(self, value):
        if isinstance(value, self._field_instance.base_class):
            key = value._primary_key
            self.set_cache_object(key, value)
            super(ForeignList, self).append(key)
        elif type(value) in [str, unicode]:
            # the value is the primary key
            # todo check to see if key is valid?
            super(ForeignList, self).append(value)
        else:
            raise TypeError('Type {actual} is not a primary key or object of {type}'.format(
                actual=type(value), type=self._field_instance.base_class))

class ForeignField(Field):

    _list_class = ForeignList

    def __init__(self, *args, **kwargs):
        super(ForeignField, self).__init__(*args, **kwargs)
        self._backref_field_name = kwargs.get('backref', None)
        self._base_class_name = args[0] # todo allow class references
        self._base_class = None

        self.object_cache = weakref.WeakKeyDictionary()

    def to_storage(self, value):
        if '_primary_key' in dir(value):
            return value._primary_key
        return value #todo deal with not lazily getting references

    @property
    def base_class(self):
        if self._base_class is None:
            self._base_class = self._parent.__class__.get_collection(self._base_class_name)
        return self._base_class

    def set_cache_object(self, instance, value):
        self.object_cache[instance] = value

    def get_cache_object(self, instance, key):
        return self.object_cache.get(instance, None)

    def __set__(self, instance, value):
        if type(value) in [str, unicode]:
            super(ForeignField, self).__set__(instance, value)
        elif isinstance(value, SchemaObject):
            self.set_cache_object(instance, value)
            super(ForeignField, self).__set__(instance, value._primary_key)
        # if self._backref_field_name is not None and not value == current_value:
        #     instance._dirty.append(
        #         ('backref', {'object_with_backref': value, 'backref_key': self._backref_field_name},)
        #     )

    def __get__(self, instance, owner):
        primary_key = super(ForeignField, self).__get__(instance, None)
        obj = self.get_cache_object(instance, primary_key)
        if not obj:
            obj = self._base_class.load(self.__get__(instance, None))
            self.set_cache_object(instance, obj)
        return obj
