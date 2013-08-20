import os
import unittest

from modularodm import StoredObject
from modularodm.storage import PickleStorage


class TestObject(StoredObject):
    def __init__(self, *args, **kwargs):
        self.set_storage(PickleStorage('Test'))
        super(TestObject, self).__init__(*args, **kwargs)


class PickleStorageTestCase(unittest.TestCase):

    def tearDown(self):
        StoredObject._clear_caches()
        try:
            os.remove('db_Test.pkl')
        except OSError:
            pass