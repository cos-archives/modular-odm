from . import Field
from ..validators import validate_float

class FloatField(Field):

    # default = 0.0
    validate = validate_float
    translate_type = float

    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)