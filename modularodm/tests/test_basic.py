import unittest
import datetime
import time
import os

from modularodm import StoredObject
from modularodm.fields.StringField import StringField
from modularodm.fields.DateTimeField import DateTimeField
from modularodm.validators import ValidationError
from modularodm.validators import MinLengthValidator
from modularodm.storage.PickleStorage import PickleStorage
from modularodm.storage.MongoStorage import MongoStorage
from modularodm.query.query import Query as Q

class Tag(StoredObject):
    _id = StringField(primary=True)
    date_created = DateTimeField(validate=True)
    date_modified = DateTimeField(validate=True, auto_now=True)
    value = StringField(default='default', validate=MinLengthValidator(5))
    keywords = StringField(default=['keywd1', 'keywd2'], validate=MinLengthValidator(5), list=True)
    _meta = {'optimistic':True}

Tag.set_storage(PickleStorage('tag'))

class BasicTests(unittest.TestCase):

    @staticmethod
    def clear_pickle_files():
        try:os.remove('db_tag.pkl')
        except:pass

    def setUp(self):
        self.clear_pickle_files()

    def tearDown(self):
        self.clear_pickle_files()

    def test_string_default(self):
        tag = Tag()
        self.assertTrue(tag.value == 'default')

    def test_stringlist_default(self):
        tag = Tag()
        self.assertTrue(tag.keywords[0] == 'keywd1')
        self.assertTrue(tag.keywords[1] == 'keywd2')

    def test_minlength_validator(self):
        tag = Tag()
        def _():
            tag.value = 'foo'
        self.assertRaises(ValidationError, _)

    # Datetime tests

    def _times_approx_equal(self, first, second, tolerance=0.01):
        diff_obj = first - second
        diff_sec = abs(diff_obj.total_seconds())
        self.assertTrue(diff_sec < tolerance)

    def test_default_datetime(self):
        tag = Tag()
        now = datetime.datetime.utcnow()
        self._times_approx_equal(tag.date_created, now)

    def test_parse_datetime(self):
        tag = Tag()
        tag.date_created = 'october 1, 1985, 10:05 am'
        self.assertEqual(tag.date_created, datetime.datetime(1985, 10, 1, 10, 5))

    def test_parse_bad_datetime(self):
        tag = Tag()
        def _():
            tag.date_created = 'cant parse this!'
        self.assertRaises(ValueError, _)

    def test_auto_now(self):
        tag = Tag()
        time.sleep(0.5)
        tag.save()
        now = datetime.datetime.utcnow()
        self._times_approx_equal(tag.date_modified, now)

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

    def test_find_match(self):
        tag = Tag()
        tag.value = 'test_query_match'
        tag.save()
        results = Tag.find(Q('value', valu='test_query_match'))
        results = list(results)
        self.assertEqual(len(results), 1)

    def test_find_match_no_result(self):
        tag = Tag()
        tag.value = 'test_query_match'
        tag.save()
        results = Tag.find(Q('value', valu='no_matches_should_be_found!'))
        results = list(results)
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()