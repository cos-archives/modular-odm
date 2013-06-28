from ..fields import Field

class ForeignField(Field):
    def __init__(self, *args, **kwargs):
        super(ForeignField, self).__init__(*args, **kwargs)
        self._backref_field_name = kwargs.get('backref', None)
        self._base_class_name = args[0] # todo allow class references

    def to_storage(self, value):
        if '_primary_key' in dir(value):
            return value._primary_key
        return None

    def __set__(self, instance, value):
        super(ForeignField, self).__set__(instance, value)
        if value is not None:
            instance._dirty.append(
                ('backref', {'object_with_backref': value, 'backref_key': self._backref_field_name},)
            )