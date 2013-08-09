from . import Field
from ..validators import validate_integer

class IntegerField(Field):

    # default = None
    validate = validate_integer
    translate_type = int

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
