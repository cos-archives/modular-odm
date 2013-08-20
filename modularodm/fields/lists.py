
class List(list):

    def __init__(self, value=None, **kwargs):

        super(List, self).__init__()

        self._field_instance = kwargs.get('field_instance', None)

        if value is None:
            return

        for item in value:
            self.append(value)

class ForeignList(List):

    def _pk(self, value):
        return self._field_instance._to_primary_key(value)

    def _to_primary_keys(self):
        return [self._pk(item) for item in super(ForeignList, self).__iter__()]

    def __iter__(self):
        if self:
            return (self[idx] for idx in range(len(self)))
        return iter([])

    def __getitem__(self, item):
        result = super(ForeignList, self).__getitem__(item)
        if isinstance(result, list):
            return [self._field_instance.base_class.load(i) for i in result]
        return self._field_instance.base_class.load(result)

    def __contains__(self, item):

        base_class = self._field_instance.base_class
        if isinstance(item, base_class):
            return item._primary_key in self._to_primary_keys()
        if isinstance(item, base_class._primary_type):
            return item in self._to_primary_keys()
        return False

    def __setitem__(self, key, value):
        super(ForeignList, self).__setitem__(key, self._pk(value))

    def insert(self, index, value):
        super(ForeignList, self).insert(index, self._pk(value))

    def append(self, value):
        super(ForeignList, self).append(self._pk(value))

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def remove(self, value):
        super(ForeignList, self).remove(self._pk(value))