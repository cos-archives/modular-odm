from . import Field
from ..validators import StringValidator

class StringField(Field):

    # default = ''
    translate_type = str
    validate = StringValidator()

    def __init__(self, *args, **kwargs):
        super(StringField, self).__init__(*args, **kwargs)