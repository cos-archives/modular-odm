from ..fields import Field
from ..validators import DateTimeValidator

import datetime

class DateTimeField(Field):

    # Method will be called on SchemaObject __init__
    default = datetime.datetime.utcnow

    validate = DateTimeValidator()

    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)
        self._auto_now = kwargs.pop('auto_now', False)

    # todo: auto_now updates datetimes on save; should there be an option to update on modify?
    def on_before_save(self, instance):
        if self._auto_now:
            self.data[instance] = self.default()