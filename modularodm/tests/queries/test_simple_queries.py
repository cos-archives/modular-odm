# -*- coding: utf-8 -*-
import logging

from modularodm import exceptions, StoredObject
from modularodm.fields import IntegerField
from modularodm.query.query import RawQuery as Q
from modularodm.tests import ModularOdmTestCase

logger = logging.getLogger(__name__)


class BasicQueryTestCase(ModularOdmTestCase):

    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField(primary=True)

        return Foo,

    def set_up_objects(self):
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
            result = self.Foo.find_one()
            logger.debug(result)

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

    def test_sort(self):
        results = self.Foo.find().sort('-_id')
        self.assertListEqual(
            [x._id for x in results],
            range(30)[::-1],
        )

    #limit_limit (order is irrelevant)

    def test_limit_offset(self):
        results = self.Foo.find().limit(10).offset(10)
        self.assertSetEqual(
            set([x._id for x in results]),
            set()
        )

    def test_limit_sort(self):
        results = self.Foo.find().limit(10).sort('-_id')
        self.assertListEqual(
            [x._id for x in results],
            range(10)[::-1],
        )

    def test_offset_limit(self):
        results = self.Foo.find().offset(10).limit(5)
        self.assertSetEqual(
            set([x._id for x in results]),
            {10, 11, 12, 13, 14}
        )

    def test_offset_offset(self):
        results = self.Foo.find().offset(10).offset(17)
        self.assertListEqual(
            [x._id for x in results],
            [27, 28, 29],
        )

    def test_offset_sort(self):
        results = self.Foo.find().offset(27).sort('-_id')
        self.assertListEqual(
            [x._id for x in results],
            [29, 28, 27],
        )

    def test_sort_limit(self):
        results = self.Foo.find().sort('-_id').limit(3)
        self.assertListEqual(
            [x._id for x in results],
            [29, 28, 27],
        )

    def test_sort_offset(self):
        results = self.Foo.find().sort('-_id').offset(27)
        self.assertListEqual(
            [x._id for x in results],
            [2, 1, 0],
        )

    def test_sort_sort(self):
        results = self.Foo.find().sort('-_id').sort('_id')
        self.assertListEqual(
            [x._id for x in results][:3],
            [0, 1, 2],
        )

    #limit_limit_* (order is irrelevant)

    def test_limit_offset_limit(self):
        results = self.Foo.find().limit(10).offset(5).limit(2)
        self.assertSetEqual(
            set([x._id for x in results]),
            {5, 6}
        )

    def test_limit_offset_limit(self):
        results = self.Foo.find().limit(10).offset(5).offset(2)
        self.assertSetEqual(
            set([x._id for x in results]),
            {7, 8, 9}
        )

    def test_limit_offset_sort(self):
        results = self.Foo.find().limit(10).offset(7).sort('-_id')
        self.assertListEqual(
            [x._id for x in results],
            [9, 8, 7],
        )

    def test_limit_sort_limit(self):
        results = self.Foo.find().limit(10).sort('-_id').limit(3)
        self.assertListEqual(
            [x._id for x in results],
            [9, 8, 7],
        )

    def test_limit_sort_offset(self):
        results = self.Foo.find().limit(10).sort('-_id').offset(7)
        self.assertListEqual(
            [x._id for x in results],
            [2, 1, 0],
        )

    def test_limit_sort_sort(self):
        results = self.Foo.find().limit(3).sort('-_id').sort('_id')
        self.assertListEqual(
            [x._id for x in results],
            [0, 1, 2],
        )

    def test_offset_limit_offset(self):
        results = self.Foo.find().offset(10).limit(5).offset(1)
        self.assertSetEqual(
            set([x._id for x in results]),
            {11, 12, 13, 14}
        )

    def test_offset_limit_sort(self):
        results = self.Foo.find().offset(10).limit(3).sort('-_id')
        self.assertListEqual(
            [x._id for x in results],
            [12, 11, 10]
        )

    def test_offset_offset_limit(self):
        results = self.Foo.find().offset(10).offset(10).limit(3)
        self.assertListEqual(
            [x._id for x in results],
            [20, 21, 22]
        )

    def test_offset_offset_sort(self):
        results = self.Foo.find().offset(10).offset(17).sort('-_id')
        self.assertListEqual(
            [x._id for x in results],
            [29, 28, 27]
        )

    def test_offset_sort_limit(self):
        results = self.Foo.find().offset(10).sort('-_id').limit(3)
        self.assertListEqual(
            [x._id for x in results],
            [29, 28, 27]
        )

    def test_offset_sort_offset(self):
        results = self.Foo.find().offset(10).sort('-_id').offset(17)
        self.assertListEqual(
            [x._id for x in results],
            [12, 11, 10]
        )

    def test_sort_limit_offset(self):
        results = self.Foo.find().sort('-_id').limit(10).offset(7)
        self.assertListEqual(
            [x._id for x in results],
            [22, 21, 20]
        )

    def test_sort_limit_sort(self):
        results = self.Foo.find().sort('-_id').limit(3).sort('_id')
        self.assertListEqual(
            [x._id for x in results],
            [27, 28, 29],
        )

    def test_sort_offset_limit(self):
        results = self.Foo.find().sort('-_id').offset(10).limit(3)
        self.assertListEqual(
            [x._id for x in results],
            [19, 18, 17]
        )

    def test_sort_offset_sort(self):
        results = self.Foo.find().sort('-_id').offset(27).sort('_id')
        self.assertListEqual(
            [x._id for x in results],
            [0, 1, 2]
        )

    def test_sort_sort_limit(self):
        results = self.Foo.find().sort('-_id').sort('_id').limit(3)
        self.assertListEqual(
            [x._id for x in results],
            [0, 1, 2]
        )

    def test_sort_sort_offset(self):
        results = self.Foo.find().sort('-_id').sort('_id').offset(27)
        self.assertListEqual(
            [x._id for x in results],
            [27, 28, 29]
        )

