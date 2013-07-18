from modm import StoredObject
from modm.fields.StringField import StringField
from modm.fields.ForeignField import ForeignField
from modm.storage.PickleStorage import PickleStorage

import pprint
pp = pprint.PrettyPrinter(indent=4)

import random
import logging

logging.basicConfig(level=logging.DEBUG)

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
    tags = ForeignField('Tag', list=True, backref='taggeds')
    tag_strings = StringField(validate=True, list=True)
    _meta = {'optimistic':True}

Tag.set_storage(PickleStorage('tag'))
Blog.set_storage(PickleStorage('blog'))

tag1 = Tag(value=str(random.randint(0,1000)), count="one")
tag1.save()

tag2 = Tag(value=str(random.randint(0,1000)), count="two")
tag2.save()

tag3 = Tag(value=str(random.randint(0,1000)), count="thr")
tag3.save()

# todo what happens when you append an object to a foreign* and the object's not saved

blog1 = Blog()
blog1.tag = tag1
blog1.tags.append(tag1)
blog1.tags.append(tag2)
blog1.tags.append(tag3)
# print [x.value for x in blog1.tags[::-1]]
blog1.save()

# logging.debug(Tag._cache)
# logging.debug(Tag.load(tag1._primary_key).tagged)
# logging.debug(tag1._backrefs)

# Test deleting a tag

blog1.tags.pop(0)
blog1.save()
#
# End test deleting a tag

# Test replacing a tag

tag4 = Tag(value=str(random.randint(0,1000)), count="for")
tag4.save()

# blog1.tag = tag2
# blog1.tags.append(tag4)
blog1.tags[0] = tag4
blog1.save()

# End test replacing a tag

# # Test clearing tags
#
# blog1.tags = []
# blog1.save()
#
# # End test clearing tags

logging.debug('tag1.tagged' + str(tag1.tagged))
#logging.debug('tag2.tagged' + str(tag2.tagged))



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

logging.debug('*** DATABASE ***\n' + pp.pformat(Tag._storage[0].store))
logging.debug('\n' + pp.pformat(Blog._storage[0].store))
logging.debug('****************')


blog1