from modularodm import exceptions, StoredObject
from modularodm.fields import IntegerField
from modularodm.query.query import RawQuery as Q
from modularodm.storage import MongoStorage, PickleStorage

import os
import pymongo
import unittest


class BasicQueryPickleTestCase(unittest.TestCase):

    make_storage = lambda x: PickleStorage('Test')

    def setUp(self):
        super(BasicQueryPickleTestCase, self).setUp()
        self.set_up_objects()

    def tearDown(self):
        self.tear_down_objects()
        super(BasicQueryPickleTestCase, self).tearDown()

    def set_up_objects(self):
        class Foo(StoredObject):
            _id = IntegerField(primary=True)

        Foo.set_storage(self.make_storage())
        Foo._clear_caches()

        self.Foo = Foo
        self.foos = []

        for idx in xrange(3):
            foo = Foo(_id=idx)
            foo.save()
            self.foos.append(foo)

    def tear_down_objects(self):
        try:
            os.remove('db_Test.pkl')
        except OSError:
            pass

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


class BasicQueryMongoTestCase(BasicQueryPickleTestCase):
    def make_storage(self):
        db = pymongo.MongoClient('mongodb://localhost:20771/').modm_test

        self.mongo_client = db

        return MongoStorage(
            db=db,
            collection='test_collection'
        )

    def tear_down_objects(self):
        try:
            self.mongo_client.drop_collection('test_collection')
        except OSError:
            pass