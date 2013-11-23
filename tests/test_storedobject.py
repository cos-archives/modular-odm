# -*- coding: utf-8 -*-
import unittest
import datetime
import os
from glob import glob

from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields, exceptions, storage
from modularodm.validators import MinLengthValidator


class Tag(StoredObject):
    _id = fields.StringField(primary=True)
    date_created = fields.DateTimeField(validate=True, auto_now_add=True)
    date_modified = fields.DateTimeField(validate=True, auto_now=True)
    value = fields.StringField(default='default', validate=MinLengthValidator(5))
    keywords = fields.StringField(default=['keywd1', 'keywd2'], validate=MinLengthValidator(5), list=True)
    _meta = {'optimistic':True}

Tag.set_storage(storage.PickleStorage('tag'))


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

class ValidateTests(unittest.TestCase):

    def test_min_length_validate(self):
        pass

    def test_max_length_validate(self):
        pass

class DefaultTests(unittest.TestCase):

    pass

class ForeignTests(unittest.TestCase):

    pass



class TestStoredObject(unittest.TestCase):

    @staticmethod
    def clear_pickle_files():
        for fname in glob("*.pkl"):
            os.remove(fname)

    def setUp(self):
        self.clear_pickle_files()

    def tearDown(self):
        for fname in glob("*.pkl"):
            os.remove(fname)

    def test_string_default(self):
        """ Make sure the default option works for StringField fields. """
        tag = Tag()
        self.assertEqual(tag.value, 'default')

    @unittest.skip('needs review')
    def test_stringlist_default(self):
        tag = Tag()
        self.assertEqual(tag.keywords[0], 'keywd1')
        self.assertEqual(tag.keywords[1], 'keywd2')

    def test_set_attribute(self):
        user = User()
        user.name = "Foo Bar"
        user.save()
        assert_equal(user.name, "Foo Bar")

    # Datetime tests

    def _times_approx_equal(self, first, second=None, tolerance=0.01):
        self.assertLess(
            abs((second or datetime.datetime.now()) - first),
            datetime.timedelta(seconds=tolerance)
        )

    def test_default_datetime(self):
        tag = Tag()
        tag.save()
        self._times_approx_equal(tag.date_created)

    @unittest.skip('needs review')
    def test_parse_datetime(self):
        tag = Tag()
        tag.date_created = 'october 1, 1985, 10:05 am'
        self.assertEqual(tag.date_created, datetime.datetime(1985, 10, 1, 10, 5))

    @unittest.skip('needs review')
    def test_parse_bad_datetime(self):
        tag = Tag()
        def _():
            tag.date_created = 'cant parse this!'
        self.assertRaises(ValueError, _)

    def test_auto_now(self):
        tag = Tag()
        tag.save()
        self._times_approx_equal(tag.date_modified)

    # Foreign tests
    def test_foreign_many_to_one_set(self):
        pass

    def test_foreign_many_to_one_replace(self):
        pass

    def test_foreign_many_to_one_del(self):
        pass

    def test_foriegn_many_to_many_set(self):
        pass

    def test_foreign_many_to_many_setitem(self):
        pass

    def test_foreign_many_to_many_insert(self):
        pass

    def test_foreign_many_to_many_append(self):
        pass

    # Query tests

    def test_find_all(self):
        pass

    def test_find_one_no_results(self):
        pass

    def test_find_one_multiple_results(self):
        pass

    def test_find_one_one_result(self):
        pass

    def test_find_exact_match(self):
        pass

    def test_find_value_property(self):
        pass

    def test_find_operator_method(self):
        pass

    def test_cant_have_multiple_primary_keys(self):
        with assert_raises(AttributeError):
            class BadObject(StoredObject):
                _id = fields.StringField(primary=True)
                another_id = fields.StringField(primary=True)


    def test_must_have_primary_key(self):
        with assert_raises(AttributeError):
            class NoPK(StoredObject):
                dummy = fields.StringField()

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

    def test_cannot_save_detached_object(self):
        user = User()
        user._detached = True
        assert_raises(exceptions.DatabaseError, lambda: user.save())

    def test_eq(self):
        user = User(name="Foobar")
        user.save()
        same_user = User.load(user._primary_key)
        assert_equal(user, same_user)
        different = User(name="Barbaz")
        assert_not_equal(user, different)
        assert_not_equal(None, user)

    # def test_find_match(self):
    #     tag = Tag()
    #     tag.value = 'test_query_match'
    #     tag.save()
    #     results = Tag.find(Q('value', valu='test_query_match'))
    #     results = list(results)
    #     self.assertEqual(len(results), 1)
    #
    # def test_find_match_no_result(self):
    #     tag = Tag()
    #     tag.value = 'test_query_match'
    #     tag.save()
    #     results = Tag.find(Q('value', valu='no_matches_should_be_found!'))
    #     results = list(results)
    #     self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
