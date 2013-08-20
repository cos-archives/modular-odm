from modularodm.tests import PickleStorageTestCase


class BasicQueryBase(object):
    def test_get_by_pk(self):
        """ Given a known primary key, ``.get(pk)``  should return the object.
        """
        pass

    def test_find_all(self):
        """ If no query object is passed, ``.find()`` should return all objects.
        """
        pass

    def test_find_one(self):
        """ Given a query with exactly one result record, ``.find_one()`` should
        return that object.
        """
        pass

    def test_find_one_return_zero(self):
        """ Given a query with zero result records, ``.find_one()`` should raise
         an appropriate error.
        """
        pass

    def test_find_on_return_many(self):
        """ Given a query with >1 result record, ``.find_one()`` should raise
          and appropriate error.
        """
        pass


class BasicQueryPickleTestCase(BasicQueryBase, PickleStorageTestCase):
    pass


# TODO: MongoStorageTestCase not yet implemented
# class BasicQueryMongoTestCase(BasicQueryBase, MongoStorageTestCase):
#     pass