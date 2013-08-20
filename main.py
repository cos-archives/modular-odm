# todo: warn on no default, or something
# todo: get default collection name for picklestorage, mongostorage constructors
# todo: requirements.txt
# todo: distutils

import pprint

from modularodm import StoredObject
from modularodm import fields
from modularodm import storage
from modularodm.validators import *
from modularodm.query.querydialect import DefaultQueryDialect as Q

from modularodm.translators import DefaultTranslator, JSONTranslator, StringTranslator

pp = pprint.PrettyPrinter(indent=4)

import random
import logging

logging.basicConfig(level=logging.DEBUG)

from pymongo import MongoClient
client = MongoClient()
db = client['testdb']

db.tag.remove()
db.blog.remove()

class Ron(StoredObject):

    _id = fields.DateTimeField(primary=True)

    ron_str = fields.StringField()
    ron_int = fields.IntegerField()
    ron_now = fields.DateTimeField()

Ron.set_storage(storage.PickleStorage('ron'))

ron1 = Ron()
ron1._id = datetime.datetime.now()
ron1.save()

ron2 = Ron()
ron2._id = datetime.datetime.now() + datetime.timedelta(days=1)
ron2.save()

# import pdb; pdb.set_trace()

ron3 = Ron()
ron3._id = datetime.datetime.now()
ron3.save()

# Ron._add_field('added_ron', fields.StringField())

import datetime

class Sheila(StoredObject):

    _id = fields.StringField(primary=True)
    _meta = {'optimistic' : True}

    # Simple fields
    sheila_str = fields.StringField(default='sheila', validate=True, required=True)
    sheila_int = fields.IntegerField(default=7, validate=MaxValueValidator(9))
    sheila_now = fields.DateTimeField()
    sheila_url = fields.StringField(validate=URLValidator())
    sheila_foostop = fields.StringField(required=True, validate=RegexValidator(r'foo$'), list=True)

    created = fields.DateTimeField(auto_now_add=True)
    modified = fields.DateTimeField(auto_now=True)

    # List fields
    sheila_strs = fields.StringField(list=True, validate=MinLengthValidator(5), list_validate=MinLengthValidator(3))
    sheila_nows = fields.DateTimeField(list=True)#, default=[])
    sheila_urls = fields.StringField(list=True, validate=[URLValidator(), MinLengthValidator(20)], list_validate=MinLengthValidator(2))
    sheila_ints = fields.IntegerField(list=True, validate=MinValueValidator(3), list_validate=MinLengthValidator(2))

    # Foreign fields
    sheila_ron = fields.ForeignField('Ron', backref='ron')
    sheila_rons = fields.ForeignField('Ron', backref='rons', list=True)

Sheila.set_storage(storage.PickleStorage('sheila'))

# import pdb; pdb.set_trace()

sheila1 = Sheila()
sheila1.sheila_url = None#'http://centerforopenscience.org/'
sheila1.sheila_str = 'shh'
sheila1.sheila_strs = ['abcde', 'bcdef', 'qqqqq']
sheila1.sheila_nows = [
    datetime.datetime.now() + datetime.timedelta(days=5),
    datetime.datetime.now() + datetime.timedelta(days=-5),
]
sheila1.sheila_urls = [
    'http://centerforopenscience.org/',
    'http://openscienceframework.org/',
]
sheila1.sheila_ints = [5, 3]

sheila1.sheila_ron = ron1

sheila1.sheila_rons = [ron2, ron3]
sheila1.save()

sheila1.save()

# import pdb; pdb.set_trace()
#
# Ron.remove(ron1)

# import pdb; pdb.set_trace()
#
# Sheila.remove(sheila1)

sheila1.sheila_rons = []
sheila1.save()

# import pdb; pdb.set_trace()

# sheila1.sheila_rons = [ron3, ron2]
sheila1.sheila_rons = [ron2]

# import pdb; pdb.set_trace()

sheila1.save()

# import pdb; pdb.set_trace()

sheila1.sheila_ron = ron2
# import pdb; pdb.set_trace()
sheila1.save()

# import pdb; pdb.set_trace()

sheila1.sheila_rons = [ron1, ron2, ron3]
sheila1.save()



sheila1_stored = sheila1.to_storage(clone=True)
sheila1_reloaded = Sheila.from_storage(sheila1_stored)

import pdb; pdb.set_trace()

class Tag(StoredObject):
    value = fields.StringField(primary=True, index=False)
    count = fields.StringField(default='c', validate=True, index=True)
    misc = fields.StringField(default='')
    misc2 = fields.StringField(default='')
    created = fields.DateTimeField(validate=True)
    modified = fields.DateTimeField(validate=True, auto_now=True)
    keywords = fields.StringField(default=['keywd1', 'keywd2'], validate=[MinLengthValidator(5), MaxLengthValidator(10)], list=True)
    mybool = fields.BooleanField(default=False)
    myint = fields.IntegerField()
    myfloat = fields.FloatField(required=True, default=4.5)
    myurl = fields.StringField(validate=URLValidator())

class Blog(StoredObject):
    _id = fields.StringField(primary=True, optimistic=True)
    body = fields.StringField(default='blog body')
    title = fields.StringField(default='asdfasdfasdf', validate=MinLengthValidator(8))
    tag = fields.ForeignField('Tag', backref='tagged')
    tags = fields.ForeignField('Tag', list=True, backref='taggeds')
    _meta = {'optimistic':True}

import os
try:os.remove('db_blog.pkl')
except:pass
try:os.remove('db_tag.pkl')
except:pass

# Tag.set_storage(storage.MongoStorage(db, 'tag'))
# Blog.set_storage(storage.MongoStorage(db, 'blog'))
Tag.set_storage(storage.PickleStorage('tag'))
Blog.set_storage(storage.PickleStorage('blog'))

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

blog1 = Blog(title='blogtitle1')
blog2 = Blog(title='blogtitle2')
blog3 = Blog(title='blogtitle3')

# blog1.tags = [tag1, tag2, tag3]
# blog1.save()

# import pdb; pdb.set_trace()
#
# StoredObject._clear_caches()
# blog1_loaded = Blog.load(blog1._id)

# import pdb; pdb.set_trace()

blog1.tags.append(tag1)
blog1.tags.append(tag1)
# blog1.tags = [tag1, tag1]

# blog1.tag = tag1

# import pdb; pdb.set_trace()
blog1.save()

blog1.tags.pop()

blog1.save()

# import pdb; pdb.set_trace()

blog2.tag = tag1
# blog2.tags.append(tag1)

blog2.save()

blog3.tag = tag1

blog3.save()

blog4 = Blog(tags=[tag1])
blog4.save()

# import pdb; pdb.set_trace()

res = Tag.find(Q('count', 'startswith', 'count_') & Q('misc', 'endswith', 'bar'))

# todo: accept list of strings
res = Tag.find_all().sort('misc2', '-misc')
# import pdb; pdb.set_trace()
print 'here', [(r.misc, r.misc2) for r in res]

res = Tag.find(Q('count', 'eq', 'count_1'))
print 'here', res.count(), list(res)

res = Tag.find(~Q('count', 'eq', 'count_1'))
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