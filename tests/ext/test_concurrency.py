import unittest
from nose.tools import *

from modularodm.ext import concurrency


class GlobalKeyedObject(concurrency.BaseKeyedObject):

    @property
    def key(self):
        return global_key


class GlobalKeyedData(GlobalKeyedObject):

    data = concurrency.KeyedProperty()


class TestConcurrency(unittest.TestCase):

    def setUp(self):
        global global_key
        global_key = None
        self.keyed_object = GlobalKeyedObject()
        self.keyed_data = GlobalKeyedData()

    def test_key(self):
        global global_key
        global_key = 'foo'
        assert_equals(self.keyed_object.key, 'foo')

    def test_keyed_property(self):
        global global_key
        global_key = 'foo'
        self.keyed_data.data = 'bar'
        assert_equal(self.keyed_data.data, 'bar')
        global_key = 'bar'
        self.keyed_data.data = 'baz'
        assert_equal(self.keyed_data.data, 'baz')
        global_key = 'foo'
        assert_equal(self.keyed_data.data, 'bar')

    def test_keyed_property_missing(self):
        global global_key
        global_key = 'foo'
        assert_equal(self.keyed_data.data, None)


if __name__ == '__main__':
    unittest.main()
