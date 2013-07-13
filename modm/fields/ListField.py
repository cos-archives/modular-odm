from ..fields import Field, List

import copy

class ListField(Field):
    def __init__(self, field_instance):
        super(self.__class__, self).__init__()

        # ListField is a list of the following (e.g., ForeignFields)
        self._field_instance = field_instance

        # Descriptor data is this type of list
        self._list_class = self._field_instance._list_class

        # Descriptor data is this type of list object, instantiated as our
        # default
        self._default = self._list_class(field_instance=self._field_instance)

    def __set__(self, instance, value):
        if isinstance(value, self._default.__class__):
            self.data[instance] = value
        elif isinstance(value, list):
            self.data[instance] = self._list_class(value, field_instance=self._field_instance)
        else:
            self.data[instance] = value

    def to_storage(self, value):
        if value:
            return [self._field_instance.to_storage(i) for i in value]
        return []

