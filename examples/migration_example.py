from modularodm.StoredObject import StoredObject
from modularodm.fields.StringField import StringField
from modularodm.fields.DictionaryField import DictionaryField
from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.ForeignField import ForeignField
from modularodm.fields.MetaDataField import MetaDataField
from modularodm.storage.PickleStorage import PickleStorage

import os
import glob

[os.remove(path) for path in glob.glob('*.pkl')]

class Tag(StoredObject):
    _id = StringField()
    count = IntegerField()
    keyword = ForeignField('keyword')
    _metadata = MetaDataField(version=1)

class Blog(StoredObject):

    _id = StringField()
    title = StringField()
    content = StringField()
    tag = ForeignField('Tag', backref='tagged')
    _metadata = MetaDataField(version=1)

Blog.set_storage(PickleStorage('blog'))

blog1 = Blog(_id='One')
blog1.save()
print blog1.to_storage()

Blog.load('One')