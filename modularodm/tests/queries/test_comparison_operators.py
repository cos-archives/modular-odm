from modularodm.tests import PickleStorageTestCase


class ComparisonOperatorsBase(object):
    def test_eq(self):
        """ Finds objects with the attribute equal to the parameter."""
        pass

    def test_ne(self):
        """ Finds objects with the attribute not equal to the parameter."""
        pass

    def test_gt(self):
        """ Finds objects with the attribute greater than the parameter."""
        pass

    def test_gte(self):
        """ Finds objects with the attribute greater than or equal to the
        parameter.
        """
        pass

    def test_lt(self):
        """ Finds objects with the attribute less than the parameter."""
        pass

    def test_lte(self):
        """ Finds objects with the attribute less than or equal to the
        parameter."""
        pass

    def test_in(self):
        """ Finds objects with the parameter in the attribute."""
        pass

    def test_nin(self):
        """ Finds objects with the parameter not in the attribute."""
        pass


# TODO: The following are defined in MongoStorage, but not PickleStorage:
#   'mod',
#   'all',
#   'size',
#   'exists',
#   'not'


class ComparisonOperatorsPickleTestCase(
    ComparisonOperatorsBase,
    PickleStorageTestCase,
):
    pass


# TODO: MongoStorageTestCase not yet implemented
# class ComparisonOperatorsMongoTestCase(
#   ComparisonOperatorsBase,
#   MongoStorageTestCase
# ):
#     pass