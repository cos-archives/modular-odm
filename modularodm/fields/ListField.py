from ..fields import Field, List
from ..validators import validate_list

class ListField(Field):

    validate = validate_list

    def __init__(self, field_instance, **kwargs):

        super(self.__class__, self).__init__(**kwargs)

        self._list_validate, self.list_validate = self._prepare_validators(kwargs.get('list_validate', False))

        # ListField is a list of the following (e.g., ForeignFields)
        self._field_instance = field_instance

        # Descriptor data is this type of list
        self._list_class = self._field_instance._list_class

        # Descriptor data is this type of list object, instantiated as our
        # default
        if self._default and not hasattr(self._default, '__iter__'):
            raise Exception(
                'Default value for list fields must be a list; received <{0}>'.format(
                    repr(self._field_instance._default)
                )
            )

        # Default is a callable that returns an empty instance of the list class
        # Avoids the need to deepcopy default values for lists, which will break
        # e.g. when validators contain (un-copyable) regular expressions.
        self._default = lambda: self._list_class(None, field_instance=self._field_instance)

    def __set__(self, instance, value):
        if isinstance(value, self._default.__class__):
            self.data[instance] = value
        elif hasattr(value, '__iter__'):
            self.data[instance] = self._list_class(field_instance=self._field_instance)
            self.data[instance].extend(value)
        else:
            self.data[instance] = value

    def do_validate(self, value):

        # Child-level validation
        for part in value:
            self._field_instance.do_validate(part)

        # Field-level list validation
        if hasattr(self.__class__, 'validate'):
            self.__class__.validate(value)

        # # Schema-level list validation
        if self._list_validate:
            if hasattr(self.list_validate, '__iter__'):
                for validator in self.list_validate:
                    validator(value)
            elif hasattr(self.list_validate, '__call__'):
                self.list_validate(value)

        # Success
        return True

    def to_storage(self, value, translator=None):
        '''
            value will come in as a List (MutableSequence)
        '''
        if value:
            return [self._field_instance.to_storage(i, translator) for i in value]
        return []

    def from_storage(self, value, translator=None):

        if value:
            return [self._field_instance.from_storage(i, translator) for i in value]
        return []

    def on_after_save(self, parent, field_name, old_stored_data, new_value):
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
            removes = [i for i in old_stored_data if self._field_instance.from_storage(i) not in new_value]
        else:
            # raise Exception('There shouldn\'t be a diff in the first place.')
            # todo: discuss -- this point can be reached when the object is not loaded and the new value is an empty list
            additions = []
            removes = []

        for i in additions:
            self._field_instance.on_after_save(parent, field_name, None, i)
        for i in removes:
            self._field_instance.on_after_save(parent, field_name, i, None)

    @property
    def base_class(self):
        if self._field_instance is None:
            return
        if not hasattr(self._field_instance, 'base_class'):
            return
        return self._field_instance.base_class