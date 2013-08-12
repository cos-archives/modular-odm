from ..fields import Field

class DictionaryField(Field):
    translate_type = dict

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._default = kwargs.get('default', {})

