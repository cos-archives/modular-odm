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
        '''
            value will come in as a List (MutableSequence)
        '''
        if value:
            return [self._field_instance.to_storage(i) for i in value]
        return []

    def on_after_save(self, old_stored_data, new_value):
        if not hasattr(self._field_instance, 'on_after_save'):
            return

        if new_value and not old_stored_data:
            additions = new_value
            removes = []
        elif old_stored_data and not new_value:
            additions = []
            removes = old_stored_data
        elif old_stored_data and new_value:
            additions = [i for i in new_value if self._field_instance.to_storage(i) not in old_stored_data]
            removes = [i for i in old_stored_data if i not in new_value]
        else:
            raise Exception('There shouldn\'t be a diff in the first place.')

        for i in additions:
            self._field_instance.on_after_save(None, i)
        for i in removes:
            self._field_instance.on_after_save(i, None)
