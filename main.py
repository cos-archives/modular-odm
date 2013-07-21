from modularodm import StoredObject
from modularodm.fields.StringField import StringField
from modularodm.fields.DateTimeField import DateTimeField
from modularodm.fields.ForeignField import ForeignField
from modularodm.storage.PickleStorage import PickleStorage
from modularodm.validators import *

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
    count = StringField(default='one@two.thr', validate=True)
    created = DateTimeField(validate=True)
    modified = DateTimeField(validate=True, automod=True)
    keywords = StringField(default=['hihihi', 'foobar'], validate=MinLengthValidator(5), list=True)

class Blog(StoredObject):
    _id = StringField(primary=True, optimistic=True)
    body = StringField(default='blog body')
    tag = ForeignField('Tag', backref='tagged')
    tags = ForeignField('Tag', list=True, backref='taggeds')
    _meta = {'optimistic':True}

Tag.set_storage(PickleStorage('tag'))
Blog.set_storage(PickleStorage('blog'))

tag1 = Tag(value=str(random.randint(0,1000)), count='one')
tag1.keywords.append('wazaa!')
tag1.keywords.append('keywordhere')
tag1.save()

tag2 = Tag(value=str(random.randint(0,1000)), count="one@two.thr")
tag2.save()

tag3 = Tag(value=str(random.randint(0,1000)), count="one@two.thr")
tag3.save()

blog1 = Blog()
blog1.tag = tag1
blog1.tags.append(tag1)
blog1.tags.append(tag2)
blog1.tags.append(tag3)
blog1.save()

# Test deleting a tag

blog1.tags.pop(0)
blog1.save()
#
# End test deleting a tag

# Test replacing a tag

tag4 = Tag(value=str(random.randint(0,1000)), count="ofor@fiv.six")
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

logging.debug('*** QUERYING ***\n')
logging.debug(('exact match', list(Tag.find(count='one@two.thr'))))
logging.debug(('matcher from value', list(Tag.find(count__startswith='one'))))
logging.debug(('matcher from operator', list(Tag.find(created__le=datetime.datetime.utcnow()))))