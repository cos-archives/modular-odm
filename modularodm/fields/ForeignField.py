from . import Field, List
from ..StoredObject import StoredObject

import logging
import warnings

class ForeignList(List):

    def __init__(self, *args, **kwargs):
        super(ForeignList, self).__init__(*args, **kwargs)

    def _to_primary_keys(self):
        return [self._field_instance._to_primary_key(item) for item in self.data]

    def __contains__(self, item):
        # todo needs to be tested
        if isinstance(item, str): # assume item is a primary key
            return item in self._to_primary_keys()
        elif isinstance(item, StoredObject): # should do an object level comparison rather than
            return item._primary_key in self._to_primary_keys()
        else:
            return False

    def __delitem__(self, key):
        del self.data[key]

    def __setitem__(self, key, value):
        # StoredObject._must_be_loaded(value)
        super(ForeignList, self).__setitem__(key, self._field_instance._to_primary_key(value))

    def __getitem__(self, item):
        # todo we could turn this into a generator, but that's really an interface question
        result = super(ForeignList, self).__getitem__(item) # we're really just dealing with self[item]
        if isinstance(result, list):
            return [self._field_instance.base_class.load(i) for i in result]
        return self._field_instance.base_class.load(result)

    def insert(self, index, value):
        # StoredObject._must_be_loaded(value)
        super(ForeignList, self).insert(index, self._field_instance._to_primary_key(value))
        # super(ForeignList, self).insert(index, value)

    def append(self, value):
        # StoredObject._must_be_loaded(value)
        super(ForeignList, self).append(self._field_instance._to_primary_key(value))

class ForeignField(Field):

    _list_class = ForeignList

    def __init__(self, *args, **kwargs):
        super(ForeignField, self).__init__(*args, **kwargs)
        self._backref_field_name = kwargs.get('backref', None)
        self._base_class_name = args[0] # todo allow class references / callable?
        self._base_class = None

    def on_after_save(self, parent, field_name, old_stored_data, new_value):
        '''
            None, Obj = go from nothing or add
            Obj, None = means go to nothing or remove
            Obj, Obj = remove then add or swap
        '''

        if self._backref_field_name == None:
            return

        if old_stored_data is not None:
            old_value = self.base_class.load(old_stored_data)
            old_value._remove_backref(self._backref_field_name, parent, field_name)

        if new_value is not None:
            new_value._set_backref(self._backref_field_name, field_name, parent)

    def to_storage(self, value, translator=None):

        if value is None:
            return value
        if '_primary_key' in dir(value):
            value_to_store = value._primary_key
        else:
            value_to_store = value
        _foreign_pn = self.base_class._primary_name
        return self.base_class._fields[_foreign_pn].to_storage(value_to_store, translator)
        # return value #todo deal with not lazily getting references

    def from_storage(self, value, translator=None):

        if value is None:
            return None
        _foreign_pn = self.base_class._primary_name
        _foreign_pk = self.base_class._fields[_foreign_pn].from_storage(value, translator)
        return _foreign_pk

    def _to_primary_key(self, value):
        if value is None:
            return None
        if isinstance(value, self.base_class):
            if not value._is_loaded:
                raise Exception('Record must be loaded.')
            return value._primary_key
        pk_type = self.base_class._fields[self.base_class._primary_name].translate_type
        if isinstance(value, pk_type):
            return value
        else:
            raise TypeError('Type {actual} is not a primary key or object of {type}'.format(
                actual=type(value), type=self.base_class))

    @property
    def base_class(self):
        if self._base_class is None:
            self._base_class = StoredObject.get_collection(self._base_class_name)
        return self._base_class

    def __set__(self, instance, value):
        if instance._detached:
            warnings.warn('Accessing a detached record.')
        # if isinstance(value, StoredObject):
        #     StoredObject._must_be_loaded(value)
        super(ForeignField, self).__set__(instance, self._to_primary_key(value))

    def __get__(self, instance, owner):
        if instance._detached:
            warnings.warn('Accessing a detached record.')
        primary_key = super(ForeignField, self).__get__(instance, None)
        if primary_key is None:
            return
        return self.base_class.load(primary_key)
