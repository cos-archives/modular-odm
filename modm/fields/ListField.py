from ..fields import Field, List

import copy

class ListField(Field):
    def __init__(self, field_instance):
        super(self.__class__, self).__init__()
        self._field_instance = field_instance
        self._default = self._field_instance._list_class(field_instance=self._field_instance)

    def __set__(self, instance, value):
        if isinstance(value, list) and not isinstance(value, List):
            for i in value:
                self.modified_data[instance].append(i)
        else:
            self.modified_data[instance] = value

    def to_storage(self, value):
        if value:
            return [self._field_instance.to_storage(i) for i in value]
        return []

