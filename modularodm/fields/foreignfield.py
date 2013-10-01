from . import Field
from .lists import ForeignList

class ForeignField(Field):

    _list_class = ForeignList

    def __init__(self, *args, **kwargs):
        super(ForeignField, self).__init__(*args, **kwargs)
        self._backref_field_name = kwargs.get('backref', None)
        self._base_class_name = args[0] # todo allow class references / callable?
        self._base_class = None
        self._is_foreign = True

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
        try:
            value_to_store = value._primary_key
        except AttributeError:
            value_to_store = value
        _foreign_pn = self.base_class._primary_name
        return self.base_class._fields[_foreign_pn].to_storage(value_to_store, translator)

    def from_storage(self, value, translator=None):

        if value is None:
            return None
        _foreign_pn = self.base_class._primary_name
        _foreign_pk = self.base_class._fields[_foreign_pn].from_storage(value, translator)
        return _foreign_pk

    def _to_primary_key(self, value):
        """
        Return primary key; if value is StoredObject, verify
        that it is loaded.

        """
        if value is None:
            return None
        if isinstance(value, self.base_class):
            if not value._is_loaded:
                raise Exception('Record must be loaded.')
            return value._primary_key

        return self.base_class._to_primary_key(value)
        # return self.base_class._check_pk_type(value)

    @property
    def mutable(self):
        return self.base_class._fields[self.base_class._primary_name].mutable

    @property
    def base_class(self):
        if self._base_class is None:
            # Look up base class in collections of attached schema; all
            # schemas share collections
            self._base_class = self._schema_class.get_collection(self._base_class_name)
        return self._base_class

    def __set__(self, instance, value, safe=False, literal=False):
        # if instance._detached:
        #     warnings.warn('Accessing a detached record.')
        value_to_set = value if literal else self._to_primary_key(value)
        super(ForeignField, self).__set__(
            instance,
            value_to_set,
            safe=safe
        )

    def __get__(self, instance, owner):
        # if instance._detached:
        #     warnings.warn('Accessing a detached record.')
        primary_key = super(ForeignField, self).__get__(instance, None)
        if primary_key is None:
            return
        return self.base_class.load(primary_key)
