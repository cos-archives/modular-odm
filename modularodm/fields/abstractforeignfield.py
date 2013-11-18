from . import Field
from .lists import AbstractForeignList

class AbstractForeignField(Field):

    _list_class = AbstractForeignList
    _is_foreign = True
    _uniform_translator = False

    def __init__(self, *args, **kwargs):
        super(AbstractForeignField, self).__init__(*args, **kwargs)
        self._backref_field_name = kwargs.get('backref', None)
        self._is_foreign = True

    def on_after_save(self, parent, field_name, old_stored_data, new_value):
        """Update back-references after save; remove self from back-reference
        list of old referent and add self to back-reference list of new
        referent.

        :param parent: Parent StoredObject instance
        :param field_name: Name of parent field mapped to self
        :param old_stored_data: Old referent of foreign field
        :param new_value: New referent of foreign field

        """
        if self._backref_field_name is None:
            return

        if old_stored_data is not None:
            old_value = self.get_foreign_object(old_stored_data)
            old_value._remove_backref(self._backref_field_name, parent, field_name)

        if new_value is not None:
            new_value._set_backref(self._backref_field_name, field_name, parent)

    def get_schema_class(self, schema):
        return self._schema_class.get_collection(schema)

    def get_primary_field(self, schema):
        schema_class = self.get_schema_class(schema)
        return schema_class._fields[schema_class._primary_name]

    def get_foreign_object(self, value):
        return self.get_schema_class(value[1])\
            .load(value[0])

    def to_storage(self, value, translator=None):

        if value is None:
            return None
        return (
            self.get_primary_field(value[1])\
                .to_storage(value[0], translator),
            value[1]
        )

    def from_storage(self, value, translator=None):

        if value is None:
            return None
        return (
            self.get_primary_field(value[1])\
                .from_storage(value[0], translator),
            value[1]
        )

    def _to_primary_key(self, value):

        if value is None:
            return None
        if hasattr(value, '_primary_key'):
            return value._primary_key

    def __set__(self, instance, value, safe=False, literal=False):
        if hasattr(value, '_primary_key'):
            value = (
                value._primary_key,
                value._name
            )
        elif isinstance(value, tuple) or isinstance(value, list):
            if len(value) != 2:
                raise ValueError('Value must have length 2')
        elif value is not None:
            raise TypeError('Value must be StoredObject, tuple, or None')
        super(AbstractForeignField, self).__set__(
            instance, value, safe=safe, literal=literal
        )

    def __get__(self, instance, owner, check_dirty=True):
        value = super(AbstractForeignField, self).__get__(
            instance, None, check_dirty
        )
        if value is None:
            return None
        return self.get_foreign_object(value)
