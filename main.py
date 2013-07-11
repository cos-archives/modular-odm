from modm import StoredObject
from modm.fields.StringField import StringField
from modm.fields.ForeignField import ForeignField
from modm.storage.PickleStorage import PickleStorage

import pprint
pp = pprint.PrettyPrinter(indent=4)

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
    tag_strings = StringField(validate=True, list=True)
    _meta = {'optimistic':True}

Tag.set_storage(PickleStorage('tag'))
Blog.set_storage(PickleStorage('blog'))

import random
tag1 = Tag(value=str(random.randint(0,1000)))
tag1.save()

tag2 = Tag(value=str(random.randint(0,1000)))
tag2.save()

tag3 = Tag(value=str(random.randint(0,1000)))
tag3.save()

blog1 = Blog()
blog1.tag = tag1
blog1.tags.append(tag1)
blog1.tags.append(tag2)
blog1.tags.append(tag3)
print [x.value for x in blog1.tags[::-1]]
blog1.save()

pk = blog1._primary_key
del blog1

blog1 = Blog.load(pk)
blog1.tag = tag1
blog1.save()

# use for testing Blog.__dict__['tag'].modified_data[blog1]

# b = Blog.load('Vj8I3')
# b.tags.append(tag1)
# b.save()
# print Blog.load('Vj8I3').tags[0]
# print Blog.load('Vj8I3').tags[0:1]
# print Blog.load('Vj8I3').tags[0]
# print Blog.load('Vj8I3').tags
# print Blog.load('Vj8I3').tags[0:1]
# print Tag.load('my first tag').value

# print tag1.tagged

print '*** DATABASE ***'
pp.pprint(Tag._storage[0].store)
pp.pprint(Blog._storage[0].store)
print '****************'