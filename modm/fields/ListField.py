from ..fields import Field

import copy

class SchemaDictList(list):
    def append(self, x):
        super(SchemaDictList, self).append(x)

class ListField(Field):
    def __init__(self, *args, **kwargs):
        print 'super init'
        super(ListField, self).__init__(*args, **kwargs)

        self._base_object = args[0]
        print '***', self._base_object, self._base_object.__class__
        self._base_class = self._base_object.__class__

        #todo move this above super, and then wrap user default in array
        self._default = kwargs.get('default', [])
        print 'setting def', self._default

    def to_storage(self, value):
        if value:
            return [self._base_object.to_storage(i) for i in value]
        return []

