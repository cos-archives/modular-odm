# -*- coding: utf-8 -*-

import unittest
from nose.tools import *

from flask import Flask

from modularodm.ext import odmflask


class TestConcurrency(unittest.TestCase):

    def setUp(self):
        self.app = Flask('test')
        self.keyed_object = odmflask.FlaskKeyedObject()
        self.keyed_cache = odmflask.FlaskCache()
        self.context = self.app.test_request_context()

    def test_key_default(self):
        assert_equal(self.keyed_object.key, odmflask.dummy_request)

    def test_key_request_context(self):
        self.context.push()
        assert_equal(self.keyed_object.key, self.context.request)

    def test_keyed_property(self):
        self.keyed_cache.data['foo'] = 'bar'
        assert_equal(self.keyed_cache.data['foo'], 'bar')
        self.context.push()
        self.keyed_cache.data['foo'] = 'bob'
        assert_equal(self.keyed_cache.data['foo'], 'bob')
        self.context.pop()
        assert_equal(self.keyed_cache.data['foo'], 'bar')

    def test_keyed_property_missing(self):
        self.context.push()
        assert_equal(self.keyed_cache.data, {})


if __name__ == '__main__':
    unittest.main()
