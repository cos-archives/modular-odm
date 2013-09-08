from modularodm import StoredObject
from modularodm.storedobject import ContextLogger
from modularodm import fields
from modularodm import storage

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

class CacheContext(object):
    def __init__(self, cache_label):
        self.cache_label = cache_label

    def __enter__(self):
        print 'entering'
        self.cached = db.cache.find_one(self.cache_label)
        if self.cached == None:
            StoredObject._clear_caches()
        else:
            for so_type, value in self.cached['cache']:
                for pk, obj in value.items():
                    pass # load
        print 'cache', self.cached

    def __exit__(self, exc_type, exc_val, exc_tb):
        print 'exiting'
        if self.cached == None:
            cache_dict = {}
            for so_type, value in StoredObject._object_cache.items():
                if so_type not in cache_dict:
                    cache_dict[so_type] = {}
                for pk, obj in value.items():
                    # obj._cache_refs.append(self.cache_label)
                    cache_dict[so_type] = obj.to_storage()
            print 'building cache', cache_dict
            db.cache.insert({'_id':self.cache_label, 'cache':cache_dict})


class Tag(StoredObject):

    _id = fields.StringField(primary=True)
    count = fields.IntegerField()

Tag.set_storage(storage.MongoStorage(db, 'tag'))

user = 'xyz'
with CacheContext('profile_' + user):
    tag = Tag(_id='tag1')
    tag.save()



