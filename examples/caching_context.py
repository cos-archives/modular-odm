from modularodm import StoredObject
from modularodm.storedobject import ContextLogger
from modularodm import fields
from modularodm import storage
from modularodm.cache.context import CacheContext

import pprint
import random
import logging

pp = pprint.PrettyPrinter(indent=4)

logging.basicConfig(level=logging.DEBUG)

from pymongo import MongoClient
client = MongoClient(port=20771)
db = client['testdb']

db.tag.remove()
db.blog.remove()
db.cache.remove()

# class CacheContext(object):
#     def __init__(self, cache_label):
#         self.cache_label = cache_label
#
#     def __enter__(self):
#         StoredObject._clear_caches()
#         self.cached = StoredObject._deep_cache.find_one({'_id' : self.cache_label})
#         if self.cached is not None:
#             for schema, records in self.cached['cache'].items():
#                 schema_class = StoredObject.get_collection(schema)
#                 for key, record in records.items():
#                     schema_class(_is_loaded=True, **schema_class.from_storage(record))
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.cached is None:
#             for schema, records in StoredObject._object_cache.raw.items():
#                 for key, record in records.items():
#                     if self.cache_label not in record._caches:
#                         record._caches.append(self.cache_label)
#                         record.save(_pop_deep_cache=False)
#             StoredObject._deep_cache.insert({
#                 '_id':self.cache_label,
#                 'cache':StoredObject._cache.raw
#             })

StoredObject._deep_cache = db.cache

class Tag(StoredObject):

    _id = fields.StringField(primary=True)
    count = fields.IntegerField()

Tag.set_storage(storage.MongoStorage(db, 'tag'))

tags = []

user = 'xyz'
with CacheContext('profile_' + user, klass=StoredObject):

    for idx in range(5):
        tag = Tag(_id=str(idx))
        tags.append(tag)
        tag.save()

tags[0].count = 7
tags[0].save()

from modularodm.query.querydialect import DefaultQueryDialect as Q

# Tag.remove(Q('_id', 'eq', tags[1]._id))
Tag.update(Q('_id', 'gte', '4'), {'count' : 42})

with CacheContext('profile_' + user, klass=StoredObject):

    print 'here'
    print StoredObject._cache.raw['tag'].keys()

print 'hi'
