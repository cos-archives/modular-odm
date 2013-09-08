import inspect
import os
import pymongo
import unittest
from StringIO import StringIO
try:
    import cpickle as pickle
except ImportError:
    import pickle
import uuid

from modularodm import StoredObject
from modularodm.storage import MongoStorage, PickleStorage


class EphemeralStorage(PickleStorage):
    def __init__(self, *args, **kwargs):
        self.store = {}
        self.fp = StringIO()

    def flush(self):
        pickle.dump(self.store, self.fp, -1)


class TestObject(StoredObject):
    def __init__(self, *args, **kwargs):
        self.set_storage(PickleStorage('Test'))
        super(TestObject, self).__init__(*args, **kwargs)


class EphemeralStorageMixin(object):
    fixture_suffix = 'Ephemeral'

    def make_storage(self):
        return EphemeralStorage()

    def clean_up_storage(self):
        pass


class PickleStorageMixin(object):
    fixture_suffix = 'Pickle'

    def make_storage(self):
        try:
            self.pickle_files
        except AttributeError:
            self.pickle_files = []

        filename = str(uuid.uuid4())[:8]
        self.pickle_files.append(filename)
        return PickleStorage(filename)

    def clean_up_storage(self):
        for f in self.pickle_files:
            try:
                os.remove('db_{}.pkl'.format(f))
            except OSError:
                pass


class MongoStorageMixin(object):
    fixture_suffix = 'Mongo'

    def make_storage(self):
        db = pymongo.MongoClient('mongodb://localhost:20771/').modm_test

        self.mongo_client = db

        try:
            self.mongo_collections
        except AttributeError:
            self.mongo_collections = []

        collection = str(uuid.uuid4())[:8]
        self.mongo_collections.append(collection)
        print self.mongo_collections

        return MongoStorage(
            db=db,
            collection=collection
        )

    def clean_up_storage(self):
        for c in self.mongo_collections:
            self.mongo_client.drop_collection(c)


class MultipleBackendMeta(type):
    def __new__(mcs, name, bases, dct):


        if name == 'ModularOdmTestCase':
            return type.__new__(
                mcs,
                name,
                bases,
                dct
            )

        frame = inspect.currentframe().f_back

        for mixin in (
            PickleStorageMixin,
            MongoStorageMixin,
            EphemeralStorageMixin,
        ):
            new_name = '{}{}'.format(name, mixin.fixture_suffix)
            frame.f_globals[new_name] = type.__new__(
                mcs,
                new_name,
                (mixin, ) + bases,
                dct
            )



class ModularOdmTestCase(unittest.TestCase):

    __metaclass__ = MultipleBackendMeta

    # Setup

    def setUp(self):
        super(ModularOdmTestCase, self).setUp()
        test_objects = self.define_test_objects() or tuple()

        for obj in test_objects:
            obj.set_storage(self.make_storage())
            self.__setattr__(obj.__name__, obj)

        StoredObject._clear_caches()

        self.set_up_test_objects()

    def set_up_storage(self):
        super(ModularOdmTestCase, self).set_up_storage()

    def define_test_objects(self):
        try:
            super(ModularOdmTestCase, self).define_test_objects()
        except AttributeError:
            pass

    def set_up_test_objects(self):
        try:
            super(ModularOdmTestCase, self).set_up_test_objects()
        except AttributeError:
            pass

    # Teardown

    def tearDown(self):
        # Avoids error when no models defined; variables like
        # pickle_files will not be defined.
        try:
            self.clean_up_storage()
        except AttributeError:
            pass
        super(ModularOdmTestCase, self).tearDown()