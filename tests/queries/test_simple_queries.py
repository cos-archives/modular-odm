# -*- coding: utf-8 -*-
import logging

from modularodm import exceptions, StoredObject
from modularodm.fields import IntegerField
from modularodm.query.query import RawQuery as Q

from tests.base import ModularOdmTestCase

logger = logging.getLogger(__name__)


class BasicQueryTestCase(ModularOdmTestCase):

    COUNT = 30

    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField(primary=True)

        return Foo,

    def set_up_objects(self):
        self.foos = []

        for idx in xrange(self.COUNT):
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


    # individual filter tests (limit, offset, sort)

    def test_limit(self):
        """ For a query that returns > n results, `.limit(n)` should return the
         first n.
        """
        self.assertEqual(
            len(self.Foo.find().limit(10)),
            10,
        )

        self.assertEqual(
            len(self.Foo.find().limit(self.COUNT+10)),
            self.COUNT,
        )
        # TODO: test limit = 0


    def test_offset(self):
        """For a query that returns n results, ``.offset(m)`` should return
        n - m results, skipping the first m that would otherwise have been
        returned.
        """
        self.assertEqual(
            len(self.Foo.find().offset(25)),
            self.COUNT - 25,
        )
        # TODO: test offset = 0, offset > self.COUNT


    def test_sort(self):
        results = self.Foo.find().sort('-_id')
        self.assertListEqual(
            [x._id for x in results],
            range(self.COUNT)[::-1],
        )


    # paired filter tests:
    #   limit  + {limit,offset,sort}
    #   offset + {offset,sort}
    #   sort   + sort
    # each test sub tests the filters in both orders. i.e. limit + offset
    # tests .limit().offset() AND .offset().limit()

    def test_limit_limit(self):
        self.assertEqual( len(self.Foo.find().limit(5).limit(10)), 10 )
        self.assertEqual( len(self.Foo.find().limit(10).limit(5)), 5  )


    def test_limit_offset(self):
        self.assertEqual( len(self.Foo.find().limit(2).offset(2)), 2 )
        self.assertEqual( len(self.Foo.find().offset(2).limit(2)), 2 )

        tmp = 5
        limit = tmp + 5
        offset = self.COUNT - tmp
        self.assertEqual(len(self.Foo.find().limit(limit).offset(offset)), tmp)
        self.assertEqual(len(self.Foo.find().offset(offset).limit(limit)), tmp)


    def test_limit_sort(self):
        limit, sort, = [10, '-_id']
        expect = range(self.COUNT-limit, self.COUNT)[::-1]

        results = self.Foo.find().limit(limit).sort(sort)
        self.assertListEqual([x._id for x in results], expect)

        results = self.Foo.find().sort(sort).limit(limit)
        self.assertListEqual([x._id for x in results], expect)


    def test_offset_offset(self):
        self.assertEqual(
            len(self.Foo.find().offset(10).offset(17)),
            self.COUNT-17
        )
        self.assertEqual(
            len(self.Foo.find().offset(17).offset(10)),
            self.COUNT-10
        )


    def test_offset_sort(self):
        offset, sort = [27, '-_id']
        expect = range(self.COUNT-offset)[::-1]

        results = self.Foo.find().offset(offset).sort(sort)
        self.assertListEqual([x._id for x in results], expect)

        results = self.Foo.find().sort(sort).offset(offset)
        self.assertListEqual([x._id for x in results], expect)


    def test_sort_sort(self):
        results = self.Foo.find().sort('-_id').sort('_id')
        self.assertListEqual(
            [x._id for x in results],
            range(self.COUNT),
        )
        results = self.Foo.find().sort('_id').sort('-_id')
        self.assertListEqual(
            [x._id for x in results],
            range(self.COUNT)[::-1],
        )


    # all three filters together

    def test_limit_offset_sort(self):
        test_sets = [
            # limit offset sort    expect
            [ 10,   7,     '-_id', range(self.COUNT-7-10, self.COUNT-7)[::-1], ],
            [ 20,   17,    '_id',  range(17, self.COUNT),                      ],
            [ 10,   5,     '_id',  range(5, 5+10),                             ],
        ]
        for test in test_sets:
            limit, offset, sort, expect = test
            all_combinations = [
                self.Foo.find().limit(limit).offset(offset).sort(sort),
                self.Foo.find().limit(limit).sort(sort).offset(offset),
                self.Foo.find().offset(offset).limit(limit).sort(sort),
                self.Foo.find().offset(offset).sort(sort).limit(limit),
                self.Foo.find().sort(sort).limit(limit).offset(offset),
                self.Foo.find().sort(sort).offset(offset).limit(limit),
            ]

            for result in all_combinations:
                self.assertListEqual( [x._id for x in result], expect )
