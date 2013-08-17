from . import Field

class MetaDataField(Field):

    # # default = None
    # validate = validate_integer
    data_type = dict

    def __init__(self, *args, **kwargs):
        super(MetaDataField, self).__init__(*args, **kwargs)
        self._default = kwargs