from ..fields import Field, ForeignField
from ..validators import validate_list
import copy

class ListField(Field):

    validate = validate_list

    def __init__(self, field_instance, **kwargs):

        super(self.__class__, self).__init__(**kwargs)

        self._list_validate, self.list_validate = self._prepare_validators(kwargs.get('list_validate', False))

        # ListField is a list of the following (e.g., ForeignFields)
        self._field_instance = field_instance
        self._is_foreign = isinstance(field_instance, ForeignField)

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
        self._default = lambda: self._list_class(None, base_class=self._field_instance.base_class)

    def __set__(self, instance, value, safe=False, literal=False):
        self._pre_set(instance, safe=safe)
        # if isinstance(value, self._default.__class__):
        #     self.data[instance] = value
        if hasattr(value, '__iter__'):
            if literal:
                self.data[instance] = self._list_class(value, base_class=self._field_instance.base_class, literal=True)
            else:
                self.data[instance] = self._list_class(base_class=self._field_instance.base_class)
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

        # Schema-level list validation
        if self._list_validate:
            if hasattr(self.list_validate, '__iter__'):
                for validator in self.list_validate:
                    validator(value)
            elif hasattr(self.list_validate, '__call__'):
                self.list_validate(value)

        # Success
        return True

    def _get_translate_func(self, translator, direction):
        try:
            return self._translators[(translator, direction)]
        except KeyError:
            if self._is_foreign:
                base_class = self._field_instance.base_class
                primary_field = base_class._fields[base_class._primary_name]
                method = primary_field._get_translate_func(translator, direction)
            else:
                method = self._field_instance._get_translate_func(translator, direction)
            self._translators[(translator, direction)] = method
            return method

    def to_storage(self, value, translator=None):
        translator = translator or self._schema_class._translator
        if value:
            if hasattr(value, '_to_primary_keys'):
                value = value._to_primary_keys()
            method = self._get_translate_func(translator, 'to')
            if method is not None or translator.null_value is not None:
                value = [
                    translator.null_value if item is None
                    else
                    item if method is None
                    else
                    method(item)
                    for item in value
                ]
            if self._field_instance.mutable:
                return copy.deepcopy(value)
            return copy.copy(value)
        return []

    def from_storage(self, value, translator=None):
        translator = translator or self._schema_class._translator
        if value:
            method = self._get_translate_func(translator, 'from')
            if method is not None or translator.null_value is not None:
                value = [
                    None if item is translator.null_value
                    else
                    item if method is None
                    else
                    method(item)
                    for item in value
                ]
            if self._field_instance.mutable:
                return copy.deepcopy(value)
            return copy.copy(value)
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