# -*- coding: utf-8 -*-
import logging
import inspect
import os
import pymongo
import unittest
import uuid
import six

from modularodm import StoredObject
from modularodm.storage import MongoStorage, PickleStorage, EphemeralStorage

logger = logging.getLogger(__name__)

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
                os.remove('db_{0}.pkl'.format(f))
            except OSError:
                pass


class MongoStorageMixin(object):
    fixture_suffix = 'Mongo'

    # DB settings
    DB_HOST = os.environ.get('MONGO_HOST', 'localhost')
    DB_PORT = int(os.environ.get('MONGO_PORT', '27017'))

    # More efficient to set up client at the class level than to re-connect
    # for each test
    mongo_client = pymongo.MongoClient(
        host=DB_HOST,
        port=DB_PORT,
    ).modm_test

    def make_storage(self):

        try:
            self.mongo_collections
        except AttributeError:
            self.mongo_collections = []

        collection = str(uuid.uuid4())[:8]
        self.mongo_collections.append(collection)
        # logger.debug(self.mongo_collections)

        return MongoStorage(
            db=self.mongo_client,
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
            frame.f_globals[new_name].__test__ = True


@six.add_metaclass(MultipleBackendMeta)
class ModularOdmTestCase(unittest.TestCase):
    __test__ = False

    # Setup

    def setUp(self):
        super(ModularOdmTestCase, self).setUp()
        test_objects = self.define_objects() or tuple()

        for obj in test_objects:
            # Create storage backend if not explicitly set
            if not getattr(obj, '_storage', None):
                obj.set_storage(self.make_storage())
            self.__setattr__(obj.__name__, obj)

        StoredObject._clear_caches()

        self.set_up_objects()

    def set_up_storage(self):
        super(ModularOdmTestCase, self).set_up_storage()

    def define_objects(self):
        try:
            super(ModularOdmTestCase, self).define_objects()
        except AttributeError:
            pass

    def set_up_objects(self):
        try:
            super(ModularOdmTestCase, self).set_up_objects()
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
