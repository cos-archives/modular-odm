from six import string_types

from . import Field
from ..validators import validate_string

class StringField(Field):

    data_type = string_types[0]
    validate = validate_string