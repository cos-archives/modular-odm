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
    os.remove('db_tag.pkl')
except:pass
try:
    os.remove('db_cache.pkl')
except:pass
try:
    os.remove('db_keyword.pkl')
except:pass

class Cache(StoredObject):
    _id = StringField()
    content = DictionaryField()

Cache.set_storage(PickleStorage('cache'))

class CachedObject(StoredObject):

    def __init__(self, **kwargs):
        super(CachedObject, self).__init__(**kwargs)
        # tells are foreign keys to pay attention, even if no backrefs?
        self.cache_id='{}:{}'.format(self._name, self._primary_key)

    @classmethod
    def deep_load_and_collect_keys(cls, key):
        obj = cls.load(key) # use cache storage translator
        keys = [(obj.__class__, obj._primary_key, obj.to_storage())]
        for field_descriptor_name, field_descriptor_obj in obj._fields.iteritems():
            if field_descriptor_obj.__class__.__name__ == 'ForeignField':
                fkey = getattr(obj, field_descriptor_name)._primary_key
                keys.extend(deep_load_and_collect_keys(field_descriptor_obj._base_class, fkey))
            # handle lists of foreigns
        return keys

    @classmethod
    def load(self, key):
        try:
            value_from_cache = Cache.load(self.cache_id)
        except:
            pass
        super(CachedObject, self).load(key)

    def save(self):
        try:
            data = self.deep_load_and_collect_keys(self.cache_id) # {blog_xyz: {}, tag_python: {}}
        except:
            pass
        # Cache(
        #     _id=self.cache_id,
        #     content = data
        # ).save()
        super(CachedObject, self).save()

class Keyword(StoredObject):
    _id = StringField()

class Tag(StoredObject):
    _id = StringField()
    count = IntegerField()
    keyword = ForeignField('keyword')

class Blog(CachedObject):
    _id = StringField()
    title = StringField()
    tag = ForeignField('Tag', backref='tagged') # when you init, add an "on_after_save" to that class, even if it's not a cached object

Keyword.set_storage(PickleStorage('keyword'))
Tag.set_storage(PickleStorage('tag'))
Blog.set_storage(PickleStorage('blog'))

keyword1 = Keyword(_id='test')
keyword1.save()
tag1 = Tag(_id='tag1', keyword=keyword1)
tag1.save()
blog1 = Blog(_id='blog1', title="hello, world", tag=tag1)
blog1.save()
print blog1

print Blog.deep_load_and_collect_keys('blog1')