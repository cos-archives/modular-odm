from . import Field
from ..validators import validate_datetime

import datetime

class DateTimeField(Field):

    validate = validate_datetime
    data_type = datetime.datetime
    mutable = True

    def _get_auto_func(self, name, value):
        if value is True:
            return datetime.datetime.now
        elif callable(value):
            return value
        raise Exception(
            'Parameter {name} must be a boolean or a callable.'.format(
                name=name
            )
        )

    def __init__(self, *args, **kwargs):

        super(DateTimeField, self).__init__(*args, **kwargs)

        self._auto_now = kwargs.pop('auto_now', False)
        self._auto_now_add = kwargs.pop('auto_now_add', False)
        if self._auto_now and self._auto_now_add:
            raise Exception("Can't use auto_now and auto_now_add on the same field.")

        #
        if (self._auto_now or self._auto_now_add) \
                and 'editable' not in self._kwargs:
            self._editable = False

        #
        if self._auto_now:
            self._auto_now = self._get_auto_func('auto_now', self._auto_now)
        #
        if self._auto_now_add:
            self._default = self._auto_now_add = self._get_auto_func('auto_now_add', self._auto_now_add)

    def on_before_save(self, instance):
        if self._auto_now:
            self.data[instance] = self._auto_now()