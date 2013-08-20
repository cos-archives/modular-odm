from modularodm.tests import PickleStorageTestCase


class StringComparisonBase(object):
    def test_contains(self):
        """ Finds objects with the attribute containing the substring."""
        pass

    def test_icontains(self):
        """ Operates as ``contains``, but ignores case."""
        pass

    def test_startwith(self):
        """ Finds objects where the attribute begins with the substring """
        pass

    def test_endswith(self):
        """ Finds objects where the attribute ends with the substring """
        pass


# TODO: The following are defined in MongoStorage, but not PickleStorage:
#   'istartswith'
#   'iendswith',
#   'exact',
#   'iexact'


class StringComparisonPickleTestCase(
    StringComparisonBase,
    PickleStorageTestCase,
):
    pass


# TODO: MongoStorageTestCase not yet implemented
# class StringComparisonMongoTestCase(BasicQueryBase, MongoStorageTestCase):
#     pass