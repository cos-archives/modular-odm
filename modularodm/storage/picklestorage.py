from .base import Storage, KeyExistsException
from ..query.queryset import BaseQuerySet
from ..query.query import QueryGroup
from ..query.query import RawQuery
from modularodm.exceptions import MultipleResultsFound, NoResultsFound

import os
import copy

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

    def __getitem__(self, index, raw=False):
        super(PickleQuerySet, self).__getitem__(index)
        key = self.data[index][self.primary]
        if raw:
            return key
        return self.schema.load(key)

    def __iter__(self, raw=False):
        keys = [obj[self.primary] for obj in self.data]
        if raw:
            return keys
        return (self.schema.load(key) for key in keys)

    def __len__(self):
        return len(self.data)

    count = __len__

    def get_key(self, index):
        return self.__getitem__(index, raw=True)

    def get_keys(self):
        return list(self.__iter__(raw=True))

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

    def insert(self, primary_name, key, value):
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

    def update(self, query, data):
        for pk in self.find(query, by_pk=True):
            for key, value in data.items():
                self.store[pk][key] = value

    def get(self, primary_name, key):
        return copy.deepcopy(self.store[key])

    def _remove_by_pk(self, key, flush=True):
        """Retrieve value from store.

        :param key: Key

        """
        del self.store[key]
        if flush:
            self.flush()

    def remove(self, *query):
        for key in self.find(*query, by_pk=True):
            self._remove_by_pk(key, flush=False)
        self.flush()

    def flush(self):
        """ Save store to file. """
        with open(self.filename, 'wb') as fp:
            pickle.dump(self.store, fp, -1)

    def find_one(self, *query):
        results = list(self.find(*query))
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            raise NoResultsFound()
        else:
            raise MultipleResultsFound(
                'Query for find_one must return exactly one result; '
                'returned {0}'.format(len(results))
            )

    def _match(self, value, query):

        if isinstance(query, QueryGroup):

            matches = [self._match(value, node) for node in query.nodes]

            if query.operator == 'and':
                return all(matches)
            elif query.operator == 'or':
                return any(matches)
            elif query.operator == 'not':
                return not any(matches)
            else:
                raise Exception('QueryGroup operator must be <and>, <or>, or <not>.')

        elif isinstance(query, RawQuery):
            attribute, operator, argument = \
                query.attribute, query.operator, query.argument

            return operators[operator](value[attribute], argument)

        else:
            raise Exception('Query must be a QueryGroup or Query object.')

    def find(self, *query, **kwargs):
        """
        Return generator over query results. Takes optional
        by_pk keyword argument; if true, return keys rather than
        values.

        """
        if len(query) == 0:
            for key, value in self.store.iteritems():
                yield value
        else:
            if len(query) > 1:
                query = QueryGroup('and', *query)
            else:
                query = query[0]

            for key, value in self.store.items():
                if self._match(value, query):
                    if kwargs.get('by_pk'):
                        yield key
                    else:
                        yield value

    def __repr__(self):
        return str(self.store)