from modularodm.tests import PickleStorageTestCase


class LogicalOperatorsBase(object):
    def test_and(self):
        """ Finds the intersection of two or more queries."""
        pass

    def test_or(self):
        """ Finds the union of two or more queries."""
        pass

    def test_not(self):
        """ Finds the inverse of a query."""
        pass


class LogicalOperatorsPickleTestCase(
    LogicalOperatorsBase,
    PickleStorageTestCase,
):
    pass


# TODO: MongoStorageTestCase not yet implemented
# class LogicalOperatorsMongoTestCase(
#   LogicalOperatorsBase,
#   MongoStorageTestCase
# ):
#     pass