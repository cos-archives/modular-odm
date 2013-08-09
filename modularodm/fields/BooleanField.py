from . import Field
from ..validators import validate_boolean

class BooleanField(Field):

    # default = False
    validate = validate_boolean
    translate_type = bool

    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)