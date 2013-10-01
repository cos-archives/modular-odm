import weakref
import warnings
import copy

from .lists import List

class Field(object):

    default = None
    base_class = None
    _list_class = List
    mutable = False

    def _prepare_validators(self, _validate):

        if hasattr(_validate, '__iter__'):

            # List of callable validators
            validate = []
            for validator in _validate:
                if hasattr(validator, '__call__'):
                    validate.append(validator)
                else:
                    raise Exception('Validator lists must be lists of callables.')

        elif hasattr(_validate, '__call__'):

            # Single callable validator
            validate = _validate

        elif type(_validate) == bool:

            # Boolean validator
            validate = _validate

        else:

            # Invalid validator type
            raise Exception('Validators must be callables, lists of callables, or booleans.')

        return _validate, validate

    def __init__(self, *args, **kwargs):

        self._args = args
        self._kwargs = kwargs
        self._translators = {}

        # Pointer to containing ListField
        # Set in StoredObject.ObjectMeta
        self._list_container = None

        self.data = weakref.WeakKeyDictionary()

        self._validate, self.validate = \
            self._prepare_validators(kwargs.get('validate', False))

        self._default = kwargs.get('default', self.default)
        self._is_primary = kwargs.get('primary', False)
        self._list = kwargs.get('list', False)
        self._required = kwargs.get('required', False)
        self._editable = kwargs.get('editable', True)
        self._index = kwargs.get('index', self._is_primary)
        self._is_foreign = False

    def do_validate(self, value):

        # Check if required
        if value is None:
            if hasattr(self, '_required') and self._required:
                raise Exception('Value <{}> is required.'.format(self._field_name))
            return True

        # Field-level validation
        cls = self.__class__
        if hasattr(cls, 'validate') and \
                self.validate != False:
            cls.validate(value)

        # Schema-level validation
        if self._validate and hasattr(self, 'validate'):
            if hasattr(self.validate, '__iter__'):
                for validator in self.validate:
                    validator(value)
            elif hasattr(self.validate, '__call__'):
                self.validate(value)

        # Success
        return True

    def _gen_default(self):
        if callable(self._default):
            return self._default()
        return copy.deepcopy(self._default)

    def _get_translate_func(self, translator, direction):
        try:
            return self._translators[(translator, direction)]
        except KeyError:
            method_name = '%s_%s' % (direction, self.data_type.__name__)
            default_name = '%s_default' % (direction,)
            try:
                method = getattr(translator, method_name)
            except AttributeError:
                method = getattr(translator, default_name)
            self._translators[(translator, direction)] = method
            return method

    def to_storage(self, value, translator=None):
        translator = translator or self._schema_class._translator
        if value is None:
            return translator.null_value
        method = self._get_translate_func(translator, 'to')
        value = value if method is None else method(value)
        if self.mutable:
            return copy.deepcopy(value)
        return value

    def from_storage(self, value, translator=None):
        translator = translator or self._schema_class._translator
        if value == translator.null_value:
            return None
        method = self._get_translate_func(translator, 'from')
        value = value if method is None else method(value)
        if self.mutable:
            return copy.deepcopy(value)
        return value

    def _pre_set(self, instance, safe=False):
        if not self._editable and not safe:
            raise Exception('Field cannot be edited.')
        if instance._detached:
            warnings.warn('Accessing a detached record.')

    def __set__(self, instance, value, safe=False, literal=False):
        self._pre_set(instance, safe=safe)
        self.data[instance] = value

    def __get__(self, instance, owner, check_dirty=True):

        # Warn if detached
        if instance._detached:
            warnings.warn('Accessing a detached record.')

        # Reload if dirty
        if instance._dirty:
            instance._dirty = False
            instance.reload()
            
        # Impute default and return
        try:
            return self.data[instance]
        except KeyError:
            default = self._gen_default()
            self.data[instance] = default
            return default


    def _get_underlying_data(self, instance):
        """Return data from raw data store, rather than overridden
        __get__ methods. Should NOT be overwritten.
        """
        return self.data.get(instance, None)

    def __delete__(self, instance):
        self.data.pop(instance, None)
