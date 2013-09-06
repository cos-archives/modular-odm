from modularodm import exceptions, StoredObject
from modularodm.fields import IntegerField
from modularodm.query.query import RawQuery as Q
from modularodm.tests import ModularOdmTestCase

import os
import pymongo
import unittest


class BasicQueryTestCase(ModularOdmTestCase):

    def define_test_objects(self):
        class Foo(StoredObject):
            _id = IntegerField(primary=True)

        return Foo,

    def set_up_test_objects(self):
        self.foos = []

        for idx in xrange(30):
            foo = self.Foo(_id=idx)
            foo.save()
            self.foos.append(foo)

    def test_load_by_pk(self):
        """ Given a known primary key, ``.get(pk)``  should return the object.
        """
        self.assertEqual(
            self.foos[0],
            self.Foo.load(0)
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

    def test_limit(self):
        """ For a query that returns > n results, `.limit(n)` should return the
         first n.
        """
        self.assertEqual(
            len(self.Foo.find().limit(10)),
            10,
        )

    def test_offset(self):
        """For a query that returns n results, ``.offset(m)`` should return
        n - m results, skipping the first m that would otherwise have been
        returned.
        """
        results = self.Foo.find().offset(25)
        self.assertSetEqual(
            set([x._id for x in results]),
            {25, 26, 27, 28, 29}
        )

    def test_limit_offset(self):
        results = self.Foo.find().limit(10).offset(10)
        self.assertSetEqual(
            set([x._id for x in results]),
            set()
        )

    def test_offset_limit(self):
        results = self.Foo.find().offset(10).limit(5)
        self.assertSetEqual(
            set([x._id for x in results]),
            {10, 11, 12, 13, 14}
        )

    def test_offset_limit_offset(self):
        results = self.Foo.find().offset(10).limit(5).offset(1)
        self.assertSetEqual(
            set([x._id for x in results]),
            {11, 12, 13, 14}
        )

    def test_limit_offset_limit(self):
        results = self.Foo.find().limit(10).offset(5).limit(2)
        self.assertSetEqual(
            set([x._id for x in results]),
            {5, 6}
        )