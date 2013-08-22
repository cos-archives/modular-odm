import inspect
import os
import pymongo
import unittest

from modularodm import StoredObject
from modularodm.storage import MongoStorage, PickleStorage


class TestObject(StoredObject):
    def __init__(self, *args, **kwargs):
        self.set_storage(PickleStorage('Test'))
        super(TestObject, self).__init__(*args, **kwargs)


class PickleStorageMixin(object):
    fixture_suffix = 'Pickle'

    def make_storage(self):
        return PickleStorage('Test')

    def clean_up_storage(self):
        try:
            os.remove('db_Test.pkl')
        except OSError:
            pass


class MongoStorageMixin(object):
    fixture_suffix = 'Mongo'

    def make_storage(self):
        db = pymongo.MongoClient('mongodb://localhost:20771/').modm_test

        self.mongo_client = db

        return MongoStorage(
            db=db,
            collection='test_collection'
        )

    def clean_up_storage(self):
        self.mongo_client.drop_collection('test_collection')


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

        for mixin in (PickleStorageMixin, MongoStorageMixin):
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
        storage = self.make_storage()

        for obj in test_objects:
            obj.set_storage(storage)
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
        self.clean_up_storage()
        super(ModularOdmTestCase, self).tearDown()