
# todo groupby
# todo indexing

import pymongo

class QuerySet(object):

    def __init__(self, schema):

        self.schema = schema
        self.primary = schema._primary_name

    def __getitem__(self, index):

        if index < 0:
            raise IndexError('Negative indexing not supported.')
        if index >= self.count():
            raise IndexError('Index out of range.')

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def count(self):
        raise NotImplementedError

    def sort(self, *keys):
        raise NotImplementedError

    def offset(self, n):
        raise NotImplementedError

    def limit(self, n):
        raise NotImplementedError

class PickleQuerySet(QuerySet):

    def __init__(self, schema, data):

        super(PickleQuerySet, self).__init__(schema)
        self.data = list(data)

    def __getitem__(self, index):

        super(PickleQuerySet, self).__getitem__(index)
        return self.schema.load(self.data[index][self.primary])

    def __iter__(self):

        return (self.schema.load(obj[self.primary]) for obj in self.data)

    def __len__(self):

        return len(self.data)

    count = __len__

    def sort(self, *keys):
        """ Iteratively sort data by keys in reverse order. """

        for key in keys[::-1]:

            if key.startswith('-'):
                reverse = True
                key = key.lstrip('-')
            else:
                reverse = False

            self.data = sorted(self.data, key=lambda record: record[key], reverse=reverse)

        return self

    def offset(self, n):

        self.data = self.data[n:]
        return self

    def limit(self, n):

        self.data = self.data[:n]
        return self

class MongoQuerySet(QuerySet):

    def __init__(self, schema, cursor):

        super(MongoQuerySet, self).__init__(schema)
        self.data = cursor

    def __getitem__(self, index):

        super(MongoQuerySet, self).__getitem__(index)
        return self.schema.load(self.data[index][self.primary])

    def __iter__(self):

        return (self.schema.load(obj[self.primary]) for obj in self.data.clone())

    def __len__(self):

        return self.data.count(with_limit_and_skip=True)

    count = __len__

    def sort(self, *keys):

        sort_key = []

        for key in keys:

            if key.startswith('-'):
                key = key.lstrip('-')
                sign = pymongo.DESCENDING
            else:
                sign = pymongo.ASCENDING

            sort_key.append((key, sign))

        self.data = self.data.sort(sort_key)
        return self

    def offset(self, n):

        self.data = self.data.skip(n)
        return self

    def limit(self, n):

        self.data = self.data.limit(n)
        return self

class CouchQuerySet(QuerySet):

    def __init__(self):

        pass

    def __iter__(self):

        pass

    def __len__(self):

        pass

    count = __len__

    def sort(self, *keys):

        pass

    def offset(self, n):

        pass

    def limit(self, n):

        pass