import os
import unittest

from modularodm import StoredObject
from modularodm.storage.PickleStorage import PickleStorage


class TestObject(StoredObject):
    def __init__(self, *args, **kwargs):
        self.set_storage(PickleStorage('Test'))
        super(TestObject, self).__init__(*args, **kwargs)
        self._clear_caches()


class PickleStorageTestCase(unittest.TestCase):

    def tearDown(self):
        try:
            os.remove('db_Test.pkl')
        except OSError:
            pass