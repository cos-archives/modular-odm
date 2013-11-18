# -*- coding: utf-8 -*-
import os
import datetime
import unittest
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields, storage

def set_datetime():
    return datetime.datetime(1999, 1, 2, 3, 45)

class User(StoredObject):
    _id = fields.StringField(primary=True)
    date_created = fields.DateTimeField(auto_now_add=set_datetime)
    date_updated = fields.DateTimeField(auto_now=set_datetime)
    _meta = {'optimistic':True}


User.set_storage(storage.PickleStorage('fields', prefix="test_"))


class TestDateTimeField(unittest.TestCase):

    def setUp(self):
        self.user = User()
        self.user.save()

    def tearDown(self):
        os.remove('test_fields.pkl')

    def test_auto_now_utcnow(self):
        expected = set_datetime()
        assert_equal(self.user.date_updated, expected)

    def test_auto_now_add(self):
        expected = set_datetime()
        assert_equal(self.user.date_created, expected)

    def test_uncallable_auto_now_param_raises_type_error(self):
        assert_raises(TypeError,
            lambda: fields.DateTimeField(auto_now='uncallable'))

    def test_cant_use_auto_now_and_auto_now_add(self):
        assert_raises(ValueError,
            lambda: fields.DateTimeField(auto_now=datetime.datetime.now,
                            auto_now_add=datetime.datetime.utcnow))


if __name__ == '__main__':
    unittest.main()
