from . import Field
from ..validators import validate_string

class StringField(Field):

    # default = ''
    translate_type = str
    validate = validate_string

    def __init__(self, *args, **kwargs):
        super(StringField, self).__init__(*args, **kwargs)