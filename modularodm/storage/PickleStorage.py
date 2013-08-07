from ..storage import Storage
from ..storage import KeyExistsException
from ..query.queryset import BaseQuerySet
from ..query.query import QueryGroup
from ..query.query import RawQuery

import operator
import copy
import os
try:
    import cpickle as pickle
except ImportError:
    import pickle

def _eq(data, test):
    if hasattr(data, '__iter__'):
        return test in data
    return data == test

operators = {

    'eq' : _eq,
    'ne' : lambda data, test: data != test,
    'gt' : lambda data, test: data > test,
    'gte' : lambda data, test: data >= test,
    'lt' : lambda data, test: data < test,
    'lte' : lambda data, test: data <= test,
    'in' : lambda data, test: data in test,
    'nin' : lambda data, test: data not in test,

    'startswith' : lambda data, test: data.startswith(test),
    'endswith' : lambda data, test: data.endswith(test),
    'contains' : lambda data, test: test in data,
    'icontains' : lambda data, test: test.lower() in data.lower(),


}

class PickleQuerySet(BaseQuerySet):

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

class PickleStorage(Storage):
    """ Storage backend using pickle. """

    QuerySet = PickleQuerySet

    def __init__(self, collection_name,  prefix='db_', ext='pkl'):
        """Build pickle file name and load data if exists.

        :param collection_name: Collection name
        :param prefix: File prefix; defaults to 'db_'
        :param ext: File extension; defaults to 'pkl'

        """
        # Build filename
        self.filename = prefix + collection_name + '.' + ext

        # Initialize empty store
        self.store = {}

        # Load file if exists
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as fp:
                data = fp.read()
                self.store = pickle.loads(data)

    def insert(self, schema, key, value):
        """Add key-value pair to storage. Key must not exist.

        :param key: Key
        :param value: Value

        """
        if key not in self.store:
            self.store[key] = value
            self.flush()
        else:
            msg = 'Key ({key}) already exists'.format(key=key)
            raise KeyExistsException(msg)

    def update(self, schema, key, value):
        """Update value of key. Key need not exist.

        :param key: Key
        :param value: Value

        """
        self.store[key] = value
        self.flush()

    def get(self, schema, key):
        return self.store[key]

    def remove(self, key):
        """Retrieve value from store.

        :param key: Key

        """
        del self.store[key]
        self.flush()

    def flush(self):
        """ Save store to file. """
        with open(self.filename, 'wb') as fp:
            pickle.dump(self.store, fp, -1)

    def find_all(self):
        return self.store.values()

    def find_one(self, **kwargs):

        results = list(self.find(**kwargs))
        if len(results) == 1:
            return results[0]

        raise Exception(
            'Query for find_one must return exactly one result; returned {0}'.format(
                len(results)
            )
        )

    def _match(self, value, query):

        if isinstance(query, QueryGroup):

            matches = [self._match(value, node) for node in query.nodes]

            if query.operator == 'and':
                return all(matches)
            elif query.operator == 'or':
                return any(matches)
            else:
                raise Exception('QueryGroup operator must be <and> or <or>.')

        elif isinstance(query, RawQuery):

            attribute, operator, argument = \
                query.attribute, query.operator, query.argument

            return operators[operator](value[attribute], argument)

        else:

            raise Exception('Query must be a QueryGroup or Query object.')

    def find(self, *query):

        if len(query) > 1:
            query = QueryGroup('and', *query)
        else:
            query = query[0]

        for key, value in self.store.iteritems():

            if self._match(value, query):
                yield value

            # match = True
            #
            # for part in query:
            #
            #     attr, oper, valu = part.attr, part.oper, part.valu
            #     match = operators[oper](value[attr], valu)
            #
            #     if not match:
            #         break
            #
            # if match:
            #     yield value

    def __repr__(self):
        return str(self.store)