import unittest
from nose.tools import *

from modularodm.ext import concurrency


class Key(object):
    pass


global_key = Key()


def get_key():
    global global_key
    return global_key


class ProxiedClass(object):
    pass


@concurrency.with_proxies({'proxied': ProxiedClass}, get_key)
class ParentClass(object):
    pass


class TestConcurrency(unittest.TestCase):

    def setUp(self):
        self.key1, self.key2 = Key(), Key()

    def test_proxy(self):

        global global_key

        global_key = self.key1
        ParentClass.proxied.foo = 'bar'
        assert_equal(ParentClass.proxied.foo, 'bar')

        global_key = self.key2
        with assert_raises(AttributeError):
            ParentClass.proxied.foo
        ParentClass.proxied.foo = 'baz'
        assert_equal(ParentClass.proxied.foo, 'baz')

        global_key = self.key1
        assert_equal(ParentClass.proxied.foo, 'bar')


if __name__ == '__main__':
    unittest.main()
