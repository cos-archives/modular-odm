import os
import unittest
import pymongo


from modularodm import fields, StoredObject
from modularodm.query.query import RawQuery as Q
from modularodm.tests import ModularOdmTestCase


# TODO: The following are defined in MongoStorage, but not PickleStorage:
#   'istartswith'
#   'iendswith',
#   'exact',
#   'iexact'


class StringComparisonTestCase(ModularOdmTestCase):

    def define_test_objects(self):
        class Foo(StoredObject):
            _id = fields.IntegerField(primary=True)
            string_field = fields.StringField()

        return Foo,

    def set_up_test_objects(self):
        self.foos = []

        field_values = (
            'first value',
            'second value',
            'third value',
        )

        for idx in xrange(len(field_values)):
            foo = self.Foo(
                _id=idx,
                string_field=field_values[idx],
            )
            foo.save()
            self.foos.append(foo)

    def tear_down_objects(self):
        try:
            os.remove('db_Test.pkl')
        except OSError:
            pass

    def test_contains(self):
        """ Finds objects with the attribute containing the substring."""
        result = self.Foo.find(
            Q('string_field', 'contains', 'second')
        )
        self.assertEqual(len(result), 1)

    def test_icontains(self):
        """ Operates as ``contains``, but ignores case."""
        result = self.Foo.find(
            Q('string_field', 'icontains', 'SeCoNd')
        )
        self.assertEqual(len(result), 1)

    def test_startwith(self):
        """ Finds objects where the attribute begins with the substring """
        result = self.Foo.find(
            Q('string_field', 'startswith', 'second')
        )
        self.assertEqual(len(result), 1)

    def test_endswith(self):
        """ Finds objects where the attribute ends with the substring """
        result = self.Foo.find(
            Q('string_field', 'endswith', 'value')
        )
        self.assertEqual(len(result), 3)
