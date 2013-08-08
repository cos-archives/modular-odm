from ..fields import Field, List


import copy

class ListField(Field):
    def __init__(self, field_instance):
        super(self.__class__, self).__init__(list=True)

        # ListField is a list of the following (e.g., ForeignFields)
        self._field_instance = field_instance

        # Descriptor data is this type of list
        self._list_class = self._field_instance._list_class

        # Descriptor data is this type of list object, instantiated as our
        # default
        if self._field_instance._default and not hasattr(self._field_instance._default, '__iter__'):
            raise Exception(
                'Default value for list fields must be a list; received <{0}>'.format(
                    repr(self._field_instance._default)
                )
            )
        self._default = self._list_class(self._field_instance._default, field_instance=self._field_instance)

    def __set__(self, instance, value):
        if isinstance(value, self._default.__class__):
            self.data[instance] = value
        elif hasattr(value, '__iter__'):
            self.data[instance].extend(value)
        else:
            self.data[instance] = value

    def to_storage(self, value):
        '''
            value will come in as a List (MutableSequence)
        '''
        if value:
            return [self._field_instance.to_storage(i) for i in value]
        return []

    def on_after_save(self, parent, old_stored_data, new_value):
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
            # raise Exception('There shouldn\'t be a diff in the first place.')
            # todo: discuss -- this point can be reached when the object is not loaded and the new value is an empty list
            additions = []
            removes = []

        for i in additions:
            self._field_instance.on_after_save(parent, None, i)
        for i in removes:
            self._field_instance.on_after_save(parent, i, None)

    @property
    def base_class(self):
        if self._field_instance is None:
            return
        if not hasattr(self._field_instance, 'base_class'):
            return
        return self._field_instance.base_class