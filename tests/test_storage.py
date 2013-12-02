# -*- coding: utf-8 -*-
import unittest
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields, storage


class User(StoredObject):
    _id = fields.StringField(primary=True)
    _meta = {'optimistic': True}


class TestStorage(unittest.TestCase):

    def test_bad_set_storage_argument(self):
        assert_raises(TypeError, lambda: User.set_storage("foo"))


if __name__ == '__main__':
    unittest.main()
