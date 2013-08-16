from . import Field
from ..validators import validate_datetime

import datetime

class DateTimeField(Field):

    validate = validate_datetime
    data_type = datetime.datetime

    def __init__(self, *args, **kwargs):

        super(DateTimeField, self).__init__(*args, **kwargs)

        self._auto_now = kwargs.pop('auto_now', False)
        self._auto_now_add = kwargs.pop('auto_now_add', False)
        if self._auto_now and self._auto_now_add:
            raise Exception("Can't use auto_now and auto_now_add on the same field.")

        if self._auto_now or self._auto_now_add:
            self._editable = False
        if self._auto_now_add:
            self._default = datetime.datetime.now

    def on_before_save(self, instance):
        if self._auto_now:
            self.data[instance] = datetime.datetime.now()