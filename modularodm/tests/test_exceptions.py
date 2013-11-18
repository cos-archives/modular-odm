import os
from glob import glob
import unittest
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields, exceptions, storage


class User(StoredObject):
    _id = fields.StringField(primary=True)
    _meta = {"optimistic": True}
    name = fields.StringField()


class Comment(StoredObject):
    _id = fields.StringField(primary=True)
    text = fields.StringField()
    user = fields.ForeignField("user", backref="comments")
    _meta = {"optimistic": True}


User.set_storage(storage.PickleStorage("test_user", prefix=None))
Comment.set_storage(storage.PickleStorage("test_comment", prefix=None))


class TestExceptions(unittest.TestCase):

    def tearDown(self):
        for fname in glob("*.pkl"):
            os.remove(fname)

    def test_multiple_primary_keys(self):
        """ Schema definition with multiple primary keys should throw an exception. """
        pass

    def test_must_be_loaded(self):
        """ Assigning an object that has not been saved as a foreign field should throw an exception. """
        user = User()
        assert_raises(exceptions.DatabaseError, lambda: Comment(user=user))

    def test_must_be_loaded_list(self):
        """ Assigning an object that has not been saved to a foreign list field should throw an exception. """
        pass

    def test_has_storage(self):
        """ Calling save on an object without an attached storage should throw an exception. """
        class NoStorage(StoredObject):
            _id = fields.StringField(primary=True)
        obj = NoStorage()
        assert_raises(exceptions.ImproperConfigurationError,
            lambda: obj.save())

    def test_storage_type(self):
        """ Assigning a non-Storage object in set_storage should throw an exception. """
        pass

    def test_validator_is_valid(self):
        """  """
        pass
