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
    content = DictionaryField(list=True)

Cache.set_storage(PickleStorage('cache'))

class CachedObject(StoredObject):

    def __init__(self, **kwargs):
        super(CachedObject, self).__init__(**kwargs)
        # tells are foreign keys to pay attention, even if no backrefs?
        self._add_field('_cache_id', StringField())
        self._cache_id = '{}:{}'.format(self._name, self._primary_key)
        self._cache = Cache(_id=self._cache_id)

    @classmethod
    def deep_load_and_collect_keys(self, key, cls=None):
        if not cls:
            cls = self
        # import pdb; pdb.set_trace()
        obj = cls.load(key) # use cache storage translator
        keys = [{obj._name: obj.to_storage()}]
        for field_descriptor_name, field_descriptor_obj in obj._fields.iteritems():
            if field_descriptor_obj.__class__.__name__ == 'ForeignField':
                fkey = getattr(obj, field_descriptor_name)._primary_key
                keys.extend(self.deep_load_and_collect_keys(fkey, cls=field_descriptor_obj._base_class))
            # handle lists of foreigns
        return keys

    @classmethod
    def load(cls, key):
        obj = cls._load_from_cache(key)
        if obj:
            return obj

        try:
            value_from_cache = Cache.load('{}:{}'.format(cls._name, key))
            for d in value_from_cache.content:
                k = d.keys()[0]
                v = d.values()[0]
                obj = StoredObject._collections[k].from_storage(v)
                if obj._primary_key == key and k == cls._name:
                    result = obj

        except Exception as e:
            pass

        return result

    def save(self):
        # Cache(
        #     _id=self.cache_id,
        #     content = data
        # ).save()
        super(CachedObject, self).save()
        self._cache.content = self.deep_load_and_collect_keys(self._primary_key) # {blog_xyz: {}, tag_python: {}}
        self._cache.save()

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

keyword1 = Keyword(_id='keyword1')
keyword1.save()
tag1 = Tag(_id='tag1', keyword=keyword1)
tag1.save()
blog1 = Blog(_id='blog1', title="hello, world", tag=tag1)
blog1.save()

import time
tick = time.time()
print Blog.load('blog1').tag.keyword
print time.time() - tick

StoredObject._cache = {}
StoredObject._object_cache = {}

tick = time.time()
print Blog.load('blog1').tag.keyword
print time.time() - tick

# {'_id': 'keyword1'}
# 4.57763671875e-05
# {'_id': 'keyword1'}
# 0.000613927841187

# {'_id': 'keyword1'}
# 4.6968460083e-05
# {'_id': 'keyword1'}
# 0.000807046890259