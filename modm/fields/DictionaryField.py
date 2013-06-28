from ..fields import Field

class SchemaDictList(list):
    def append(self, x):
        super(SchemaDictList, self).append(x)

class DictionaryField(Field):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._default = kwargs.get('default', {})

    def to_storage(self, value):
        if value:
            return [self._base_object.to_storage(i) for i in value]
        return []

