
from modularodm import StoredObject
from modularodm import fields
from modularodm import storage

from bson import ObjectId

class Foo(StoredObject):
    _id = fields.StringField(default=lambda: str(ObjectId()))

class Bar(StoredObject):
    _id = fields.StringField(default=lambda: str(ObjectId()))

class Baz(StoredObject):
    _id = fields.StringField(default=lambda: str(ObjectId()))
    abstract = fields.AbstractForeignField(backref='abstracted')

class Bob(StoredObject):
    _id = fields.StringField(default=lambda: str(ObjectId()))
    abstract = fields.AbstractForeignField(list=True, backref='abstracted')


from pymongo import MongoClient
client = MongoClient()
collection = client['testdb']

Foo.set_storage(storage.MongoStorage(collection, 'foo'))
Bar.set_storage(storage.MongoStorage(collection, 'bar'))
Baz.set_storage(storage.MongoStorage(collection, 'baz'))
Bob.set_storage(storage.MongoStorage(collection, 'bob'))
#Foo.set_storage(storage.PickleStorage('foo'))
#Bar.set_storage(storage.PickleStorage('bar'))
#Baz.set_storage(storage.PickleStorage('baz'))
#Bob.set_storage(storage.PickleStorage('bob'))

#foo = Foo()
#foo.save()

foo_id = 'asdf'

bar = Bar()
bar.save()

baz1 = Baz(abstract=(foo_id, 'foo'))
baz1.save()

foo = Foo(_id=foo_id)
foo.save()

baz2 = Baz(abstract=bar)
baz2.save()

baz3 = Baz(abstract=foo)
baz3.save()

baz3.abstract = bar
baz3.save()

baz3.remove_one(baz3)

#Bob._clear_caches()

import pdb; pdb.set_trace()