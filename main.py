from modm import StoredObject
from modm.fields.StringField import StringField
from modm.fields.ForeignField import ForeignField
from modm.storage.PickleStorage import PickleStorage

import os

try:os.remove('db_blog.pkl')
except:pass
try:os.remove('db_tag.pkl')
except:pass

class Tag(StoredObject):
    value = StringField(primary=True)
    count = StringField(default='one')

class Blog(StoredObject):
    _id = StringField(primary=True, optimistic=True)
    body = StringField(default='blog body')
    tag = ForeignField('Tag', backref='tagged')
    tags = ForeignField('Tag', list=True)
    _meta = {'optimistic':True}

Tag.set_storage(PickleStorage('tag'))
Blog.set_storage(PickleStorage('blog'))

tag1 = Tag(value='my first tag')
tag1.save()

blog1 = Blog()
blog1.tag = tag1
blog1.save()

print '***'
print Tag._storage[0].store
print Blog._storage[0].store
print '***'