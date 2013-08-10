from modularodm.StoredObject import StoredObject
from modularodm.fields.StringField import StringField
from modularodm.fields.DictionaryField import DictionaryField
from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.ForeignField import ForeignField
from modularodm.storage.PickleStorage import PickleStorage

import os
try:
    os.remove('db_blog.pkl')
except:pass
try:
    os.remove('db_user.pkl')
except:pass

def deep_load_and_collect_keys(cls, key):
    obj = cls.load(key) # use cache storage translator
    keys = [{obj.__class__.__name__.lower():obj.to_storage()}]
    for field_descriptor_name, field_descriptor_obj in obj._fields.iteritems():
        if field_descriptor_obj.__class__.__name__ == 'ForeignField':
            fkey = getattr(obj, field_descriptor_name)._primary_key
            keys.extend(deep_load_and_collect_keys(field_descriptor_obj._base_class, fkey))
        # handle lists of foreigns
    return keys

class User(StoredObject):
    name = StringField(primary=True)

class Blog(StoredObject):
    title = StringField(primary=True)
    user = ForeignField('user')

User.set_storage(PickleStorage('user'))
Blog.set_storage(PickleStorage('blog'))

user1 = User(name='Jeff')
user1.save()

blog1 = Blog(title='hello4')
blog1.user = user1
blog1.save()

#print Blog.load('hello4')
print deep_load_and_collect_keys(Blog, 'hello4')

#print blog1._get_cached_data('hello4')