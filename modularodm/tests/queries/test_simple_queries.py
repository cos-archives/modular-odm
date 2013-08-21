from modularodm import exceptions, StoredObject
from modularodm.fields import IntegerField
from modularodm.query.query import RawQuery as Q
from modularodm.tests import ModularOdmTestCase

import os
import pymongo
import unittest


class BasicQueryPickleTestCase(ModularOdmTestCase):

    def define_test_objects(self):
        class Foo(StoredObject):
            _id = IntegerField(primary=True)

        return Foo,

    def set_up_test_objects(self):
        self.foos = []

        for idx in xrange(3):
            foo = self.Foo(_id=idx)
            foo.save()
            self.foos.append(foo)

    @unittest.skip('Not sure yet if this should be .get() or .load()')
    def test_get_by_pk(self):
        """ Given a known primary key, ``.get(pk)``  should return the object.
        """
        self.assertEqual(
            self.foos[0],
            self.Foo.get(0)
        )

    def test_find_all(self):
        """ If no query object is passed, ``.find()`` should return all objects.
        """
        self.assertEqual(
            len(self.Foo.find()),
            len(self.foos)
        )

    def test_find_one(self):
        """ Given a query with exactly one result record, ``.find_one()`` should
        return that object.
        """
        self.assertEqual(
            self.Foo.find_one(Q('_id', 'eq', 0))._id,
            self.foos[0]._id
        )

    def test_find_one_return_zero(self):
        """ Given a query with zero result records, ``.find_one()`` should raise
         an appropriate error.
        """
        with self.assertRaises(exceptions.NoResultsFound):
            self.Foo.find_one(Q('_id', 'eq', -1))

    def test_find_one_return_many(self):
        """ Given a query with >1 result record, ``.find_one()`` should raise
          and appropriate error.
        """
        with self.assertRaises(exceptions.MultipleResultsFound):
            print self.Foo.find_one()