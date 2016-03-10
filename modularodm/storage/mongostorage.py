# -*- coding: utf-8 -*_

import re
import pymongo

from .base import Storage
from ..query.queryset import BaseQuerySet
from ..query.query import QueryGroup
from ..query.query import RawQuery
from modularodm.exceptions import (
    KeyExistsException,
    MultipleResultsFound,
    NoResultsFound,
)


# From mongoengine.queryset.transform
COMPARISON_OPERATORS = ('ne', 'gt', 'gte', 'lt', 'lte', 'in', 'nin', 'mod',
                        'all', 'size', 'exists', 'not', 'elemMatch')
# GEO_OPERATORS        = ('within_distance', 'within_spherical_distance',
#                         'within_box', 'within_polygon', 'near', 'near_sphere',
#                         'max_distance', 'geo_within', 'geo_within_box',
#                         'geo_within_polygon', 'geo_within_center',
#                         'geo_within_sphere', 'geo_intersects')
STRING_OPERATORS     = ('contains', 'icontains', 'startswith',
                        'istartswith', 'endswith', 'iendswith',
                        'exact', 'iexact')
# CUSTOM_OPERATORS     = ('match',)
# MATCH_OPERATORS      = (COMPARISON_OPERATORS + GEO_OPERATORS +
#                         STRING_OPERATORS + CUSTOM_OPERATORS)

# UPDATE_OPERATORS     = ('set', 'unset', 'inc', 'dec', 'pop', 'push',
#                         'push_all', 'pull', 'pull_all', 'add_to_set',
#                         'set_on_insert')


# Adapted from mongoengine.fields
def prepare_query_value(op, value):

    if op.lstrip('i') in ('startswith', 'endswith', 'contains', 'exact'):
        flags = 0
        if op.startswith('i'):
            flags = re.IGNORECASE
            op = op.lstrip('i')

        regex = r'%s'
        if op == 'startswith':
            regex = r'^%s'
        elif op == 'endswith':
            regex = r'%s$'
        elif op == 'exact':
            regex = r'^%s$'

        # escape unsafe characters which could lead to a re.error
        value = re.escape(value)
        value = re.compile(regex % value, flags)

    return value


# TODO: Test me
def translate_query(query=None, mongo_query=None):
    """

    """
    mongo_query = mongo_query or {}

    if isinstance(query, RawQuery):
        attribute, operator, argument = \
            query.attribute, query.operator, query.argument

        if operator == 'eq':
            mongo_query[attribute] = argument

        elif operator in COMPARISON_OPERATORS:
            mongo_operator = '$' + operator
            if attribute not in mongo_query:
                mongo_query[attribute] = {}
            mongo_query[attribute][mongo_operator] = argument

        elif operator in STRING_OPERATORS:
            mongo_operator = '$regex'
            mongo_regex = prepare_query_value(operator, argument)
            if attribute not in mongo_query:
                mongo_query[attribute] = {}
            mongo_query[attribute][mongo_operator] = mongo_regex

    elif isinstance(query, QueryGroup):

        if query.operator == 'and':
            return {'$and': [translate_query(node) for node in query.nodes]}

        elif query.operator == 'or':
            return {'$or' : [translate_query(node) for node in query.nodes]}

        elif query.operator == 'not':
            # Hack: A nor A == not A
            subquery = translate_query(query.nodes[0])
            return {'$nor' : [subquery, subquery]}

        else:
            raise ValueError('QueryGroup operator must be <and>, <or>, or <not>.')

    elif query is None:
        return {}

    else:
        raise TypeError('Query must be a QueryGroup or Query object.')

    return mongo_query


class MongoQuerySet(BaseQuerySet):

    _NEGATIVE_INDEXING = True

    def __init__(self, schema, cursor):
        super(MongoQuerySet, self).__init__(schema)
        self.data = cursor
        self._order = [('_id', 1)]  # Default sorting

    def _do_getitem(self, index, raw=False):
        if isinstance(index, slice):
            return MongoQuerySet(self.schema, self.data.clone()[index])
        if index < 0:
            clone = self.data.clone().sort([(o[0], o[1] * -1) for o in self._order])
            result = clone[(index * -1) - 1]
        else:
            result = self.data[index]
        if raw:
            return result[self.primary]
        return self.schema.load(data=result)

    def __iter__(self, raw=False):
        cursor = self.data.clone()
        if raw:
            return [each[self.primary] for each in cursor]
        return (self.schema.load(data=each) for each in cursor)

    def __len__(self):
        return self.data.count(with_limit_and_skip=True)

    count = __len__

    def get_key(self, index):
        return self.__getitem__(index, raw=True)

    def get_keys(self):
        return list(self.__iter__(raw=True))

    def sort(self, *keys):
        sort_key = []

        for key in keys:

            if key.startswith('-'):
                key = key.lstrip('-')
                sign = pymongo.DESCENDING
            else:
                sign = pymongo.ASCENDING

            sort_key.append((key, sign))

        self._order = sort_key
        self.data = self.data.sort(sort_key)
        return self

    def offset(self, n):
        self.data = self.data.skip(n)
        return self

    def limit(self, n):
        self.data = self.data.limit(n)
        return self


class MongoStorage(Storage):
    """Wrap a MongoDB collection. Note: `store` is a property instead of an
    attribute to handle passing `db` as a proxy.

    :param Database db:
    :param str collection:
    """
    QuerySet = MongoQuerySet

    def __init__(self, db, collection):
        self.db = db
        self.collection = collection

    @property
    def store(self):
        return self.db[self.collection]

    def _ensure_index(self, key):
        self.store.ensure_index(key)

    def find(self, query=None, **kwargs):
        mongo_query = translate_query(query)
        return self.store.find(mongo_query)

    def find_one(self, query=None, **kwargs):
        mongo_query = translate_query(query)
        matches = self.store.find(mongo_query).limit(2)

        if matches.count() == 1:
            return matches[0]

        if matches.count() == 0:
            raise NoResultsFound()

        raise MultipleResultsFound(
            'Query for find_one must return exactly one result; '
            'returned {0}'.format(matches.count())
        )

    def get(self, primary_name, key):
        return self.store.find_one({primary_name : key})

    def insert(self, primary_name, key, value):
        if primary_name not in value:
            value = value.copy()
            value[primary_name] = key
        try:
            self.store.insert(value)
        except pymongo.errors.DuplicateKeyError:
            raise KeyExistsException

    def update(self, query, data):
        mongo_query = translate_query(query)

        # Field "_id" shouldn't appear in both search and update queries; else
        # MongoDB will raise a "Mod on _id not allowed" error
        if '_id' in mongo_query:
            update_data = {k: v for k, v in data.items() if k != '_id'}
        else:
            update_data = data
        update_query = {'$set': update_data}

        self.store.update(
            mongo_query,
            update_query,
            upsert=False,
            multi=True,
        )

    def remove(self, query=None):
        mongo_query = translate_query(query)
        self.store.remove(mongo_query)

    def flush(self):
        pass
