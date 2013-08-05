import pprint

from modularodm import StoredObject
from modularodm.fields.StringField import StringField
from modularodm.fields.DateTimeField import DateTimeField
from modularodm.fields.ForeignField import ForeignField
from modularodm.storage.PickleStorage import PickleStorage
from modularodm.storage.MongoStorage import MongoStorage
from modularodm.validators import *
from modularodm.query.query import Query as Q

pp = pprint.PrettyPrinter(indent=4)

import random
import logging

logging.basicConfig(level=logging.DEBUG)

from pymongo import MongoClient
client = MongoClient()
db = client['testdb']

db.tag.remove()
db.blog.remove()

import os
try:os.remove('db_blog.pkl')
except:pass
try:os.remove('db_tag.pkl')
except:pass

class Tag(StoredObject):
    value = StringField(primary=True)
    count = StringField(default='c', validate=True)
    misc = StringField()
    misc2 = StringField()
    created = DateTimeField(validate=True)
    modified = DateTimeField(validate=True, auto_now=True)
    keywords = StringField(default=['keywd1', 'keywd2'], validate=[MinLengthValidator(5), MaxLengthValidator(10)], list=True)

class Blog(StoredObject):
    _id = StringField(primary=True, optimistic=True)
    body = StringField(default='blog body')
    tag = ForeignField('Tag', backref='tagged')
    tags = ForeignField('Tag', list=True, backref='taggeds')
    _meta = {'optimistic':True}

Tag.set_storage(MongoStorage(db, 'tag'))
Blog.set_storage(MongoStorage(db, 'blog'))
# Tag.set_storage(PickleStorage('tag'))
# Blog.set_storage(PickleStorage('blog'))

tag1 = Tag(value=str(random.randint(0, 1000)), count='count_1', keywords=['keywd1', 'keywd3', 'keywd4'])
tag1.save()

tag2 = Tag(value=str(random.randint(0, 1000)), count="count_2", misc="foobar", misc2="a")
tag2.save()

tag3 = Tag(value=str(random.randint(0, 1000)), count="count_3", misc="foobaz", misc2="b")
tag3.save()

tag4 = Tag(value=str(random.randint(0, 1000)), count="count_4", misc="bar", misc2="a")
tag4.save()

tag5 = Tag(value=str(random.randint(0, 1000)), count="count_5", misc="baz", misc2="b")
tag5.save()

blog1 = Blog()
blog1.tag = tag1
blog1.tags.append(tag1)
blog1.tags.append(tag2)
blog1.tags.append(tag3)
blog1.save()

blog2 = Blog()
blog2.tag = tag1
blog2.tags.append(tag2)
blog2.save()

# todo: accept list of strings
res = Tag.find_all().sort('misc2', '-misc')
print 'here', [(r.misc, r.misc2) for r in res]

res = Tag.find(Q('count', 'eq', 'count_1'))
print 'here', res.count(), list(res)

res = Tag.find(Q('misc', 'startswith', 'foo'))
print 'here', res.count(), list(res)

res = Tag.find(Q('misc', 'endswith', 'bar'))
print 'here', res.count(), list(res)

# todo: alias to in
res = Tag.find(Q('keywords', 'eq', 'keywd1'))
print 'here', res.count(), list(res)

res = Tag.find(Q('keywords', 'eq', 'keywd2'))
print 'here', res.count(), list(res)

res = Tag.find(Q('keywords', 'eq', 'keywd3'))
print 'here', res.count(), list(res)

# Compound query
res = Tag.find(Q('misc', 'startswith', 'foo'), Q('keywords', 'eq', 'keywd1'))
print 'here', res.count(), list(res)

# Query by foreign key
res = Blog.find(Q('tag', 'eq', tag1))
print 'here', res.count(), list(res)

# Query by foreign list
res = Blog.find(Q('tags', 'eq', tag1))
print 'here', res.count(), list(res)

# # Test deleting a tag
#
# blog1.tags.pop(0)
# blog1.save()
# #
# # End test deleting a tag
#
# # Test replacing a tag
#
# tag4 = Tag(value=str(random.randint(0,1000)), count="ofor@fiv.six")
# tag4.save()
#
# # blog1.tag = tag2
# # blog1.tags.append(tag4)
# blog1.tags[0] = tag4
# blog1.save()
#
# # End test replacing a tag
#
# # # Test clearing tags
# #
# # blog1.tags = []
# # blog1.save()
# #
# # # End test clearing tags
#
# logging.debug('tag1.tagged' + str(tag1.tagged))
# #logging.debug('tag2.tagged' + str(tag2.tagged))
#
#
#
# # use for testing Blog.__dict__['tag'].modified_data[blog1]
#
# # b = Blog.load('Vj8I3')
# # b.tags.append(tag1)
# # b.save()
# # print Blog.load('Vj8I3').tags[0]
# # print Blog.load('Vj8I3').tags[0:1]
# # print Blog.load('Vj8I3').tags[0]
# # print Blog.load('Vj8I3').tags
# # print Blog.load('Vj8I3').tags[0:1]
# # print Tag.load('my first tag').value
#
# # print tag1.tagged
#
# logging.debug('*** DATABASE ***\n' + pp.pformat(Tag._storage[0].store))
# logging.debug('\n' + pp.pformat(Blog._storage[0].store))
# logging.debug('****************')
#
# logging.debug('*** QUERYING ***\n')
# logging.debug(('exact match', list(Tag.find(count='one@two.thr'))))
# logging.debug(('matcher from value', list(Tag.find(count__startswith='one'))))
# logging.debug(('matcher from operator', list(Tag.find(created__le=datetime.datetime.utcnow()))))