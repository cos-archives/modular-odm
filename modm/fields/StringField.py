from ..fields import Field

import weakref

class StringField(Field):

    default = ''

    def __init__(self, *args, **kwargs):
        super(StringField, self).__init__(*args, **kwargs)

    def validate(self, value):
        if isinstance(value, unicode):
            return True
        else:
            try:
                value.decode('utf-8')
                return True
            except:
                return False

    def to_storage(self, value):
        return value
