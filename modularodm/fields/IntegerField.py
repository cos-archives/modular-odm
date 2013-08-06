from ..fields import Field
from ..validators import validate_integer

class IntegerField(Field):

    default = 0
    validate = validate_integer

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)