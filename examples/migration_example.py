from modularodm.StoredObject import StoredObject
from modularodm.fields.StringField import StringField
from modularodm.fields.DictionaryField import DictionaryField
from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.ForeignField import ForeignField
from modularodm.fields.MetaDataField import MetaDataField
from modularodm.storage.PickleStorage import PickleStorage

import os
import glob
import copy

[os.remove(path) for path in glob.glob('*.pkl')]

class Tag(StoredObject):
    _id = StringField()
    count = IntegerField()
    _metadata = MetaDataField(version=1)

class Blog(StoredObject):
    _id = StringField()
    title = StringField()
    content = StringField()
    tag = ForeignField('Tag', backref='tagged')
    _metadata = MetaDataField(version=1)

Tag.set_storage(PickleStorage('tag'))
Blog.set_storage(PickleStorage('blog'))

blog1 = Blog(_id='One', title="My first blog", content="Hello, world.")
tag = Tag(_id="python")
tag.save()
blog1.tag = tag
blog1.save()
print 'BLOG V1 :', blog1.to_storage()

blog1._clear_caches('One')

BlogVersion1 = Blog

class Blog(StoredObject):
    _id = StringField()
    title = StringField()
    body = StringField()
    tag = ForeignField('Tag', backref='tagged')
    _metadata = MetaDataField(
        version=2,
        version_of="BlogVersion1"
    )

    @classmethod
    def process_migration(cls, new_data=None, old_data=None, version_of=None):
        # todo load from data should not need a registered storage?
        del new_data['content']
        new_data['body'] = old_data['content']
        return new_data

Blog.set_storage(PickleStorage('blog'))

blog1 = Blog.load('One')
print 'BLOG V2 :', blog1.to_storage()
