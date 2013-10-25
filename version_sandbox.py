# todo: warn on no default, or something
# todo: get default collection name for picklestorage, mongostorage constructors
# todo: requirements.txt

import pprint

from modularodm import StoredObject
from modularodm.storedobject import ContextLogger
from modularodm import fields
from modularodm import storage
from modularodm.validators import *
from modularodm.query.querydialect import DefaultQueryDialect as Q

from modularodm.version.context import VersionContext

pp = pprint.PrettyPrinter(indent=4)

import random
import logging
import time
import datetime

logging.basicConfig(level=logging.DEBUG)

from pymongo import MongoClient
client = MongoClient()
database = client['testdb']

database['foo'].remove()
database['foo_versioned'].remove()

class Foo(StoredObject):

    _meta = {
        'versioned': True,
        'version_method': 'full',
    }

    _id = fields.StringField(default=lambda: str(ObjectId()))
    title = fields.StringField()
    tags = fields.StringField(list=True)

Foo.set_storage(
    storage.MongoStorage(database, 'foo'),
    versioned=storage.MongoStorage(database, 'foo_versioned'),
)

#foo = Foo(title='hi')
#foo.save()
#
#dt_save0 = datetime.datetime.utcnow()
#time.sleep(2.5)
#
#foo.title = 'newtitle'
#foo.save()
#
#dt_save1 = datetime.datetime.utcnow()
#time.sleep(2.5)
#
#foo.tags = ['good', 'foo']
#foo.save()
#
#dt_save2 = datetime.datetime.utcnow()
#
#Foo._clear_caches()
#foo_old = Foo.load(foo._primary_key, date=dt_save0 - datetime.timedelta(days=1))
#
#Foo._clear_caches()
#foo_after_one_update = Foo.load(foo._primary_key, date=dt_save1)
#
#Foo._clear_caches()
#foo_after_two_updates = Foo.load(foo._primary_key, date=dt_save2)
#
#print foo_old
#print foo_after_one_update
#print foo_after_two_updates

foo1 = Foo(title='foo1')
foo1.save()

foo2 = Foo(title='foo2')
foo2.save()

time.sleep(1)

foo1.tags = ['tag1']
foo1.save()

time.sleep(1)

foo2.tags = ['tag2']
foo2.save()

with VersionContext(datetime.datetime.utcnow() - datetime.timedelta(days=1)):
    foo1_vc_old = Foo.load(foo1._primary_key)
    foo2_vc_old = Foo.load(foo2._primary_key)

with VersionContext(datetime.datetime.utcnow()):
    foo1_vc_new = Foo.load(foo1._primary_key)
    foo2_vc_new = Foo.load(foo2._primary_key)

print 'foo1'
print foo1_vc_old
print foo1_vc_new

print 'foo2'
print foo2_vc_old
print foo2_vc_new

import pdb; pdb.set_trace()
