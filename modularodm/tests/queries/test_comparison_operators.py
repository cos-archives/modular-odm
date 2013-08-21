import datetime as dt
import os
import unittest


from modularodm import fields, StoredObject
from modularodm.query.query import RawQuery as Q
from modularodm.storage import PickleStorage

# TODO: The following are defined in MongoStorage, but not PickleStorage:
#   'mod',
#   'all',
#   'size',
#   'exists',
#   'not'

# TODO: These tests should be applied to all default field types. Perhaps use an
# iterative approach?


class ComparisonOperatorsPickleTestCase(unittest.TestCase):

    make_storage = lambda x: PickleStorage('Test')

    def setUp(self):
        super(ComparisonOperatorsPickleTestCase, self).setUp()
        self.set_up_objects()

    def tearDown(self):
        self.tear_down_objects()
        super(ComparisonOperatorsPickleTestCase, self).tearDown()

    def set_up_objects(self):
        class Foo(StoredObject):
            _id = fields.IntegerField(primary=True)
            integer_field = fields.IntegerField()
            string_field = fields.StringField()
            datetime_field = fields.DateTimeField()
            float_field = fields.FloatField()
            list_field = fields.IntegerField(list=True)

        Foo.set_storage(self.make_storage())
        Foo._clear_caches()

        self.Foo = Foo
        self.foos = []

        for idx in xrange(3):
            foo = Foo(
                _id=idx,
                integer_field = idx,
                string_field = 'Value: {}'.format(idx),
                datetime_field = dt.datetime.now() + dt.timedelta(hours=idx),
                float_field = float(idx + 100.0),
                list_field = [(10 * idx) + 1, (10 * idx) + 2, (10 * idx) + 3],
            )
            foo.save()
            self.foos.append(foo)

    def tear_down_objects(self):
        try:
            os.remove('db_Test.pkl')
        except OSError:
            pass

    def test_eq(self):
        """ Finds objects with the attribute equal to the parameter."""
        self.assertEqual(
            self.Foo.find_one(
                Q('integer_field', 'eq', self.foos[1].integer_field)
            )._id,
            self.foos[1]._id,
        )

    def test_ne(self):
        """ Finds objects with the attribute not equal to the parameter."""
        self.assertEqual(
            len(self.Foo.find(
                Q('integer_field', 'ne', self.foos[1].integer_field)
            )),
            2
        )

    def test_gt(self):
        """ Finds objects with the attribute greater than the parameter."""
        result = self.Foo.find(
            Q('integer_field', 'gt', self.foos[1].integer_field)
        )
        self.assertEqual(len(result), 1)

    def test_gte(self):
        """ Finds objects with the attribute greater than or equal to the
        parameter.
        """
        result = self.Foo.find(
            Q('integer_field', 'gte', self.foos[1].integer_field)
        )
        self.assertEqual(len(result), 2)

    def test_lt(self):
        """ Finds objects with the attribute less than the parameter."""
        result = self.Foo.find(
            Q('integer_field', 'lt', self.foos[1].integer_field)
        )
        self.assertEqual(len(result), 1)

    def test_lte(self):
        """ Finds objects with the attribute less than or equal to the
        parameter."""
        result = self.Foo.find(
            Q('integer_field', 'lte', self.foos[1].integer_field)
        )
        self.assertEqual(len(result), 2)

    def test_in(self):
        """ Finds objects with the parameter in the attribute."""
        result = self.Foo.find(
            Q('integer_field', 'in', [1, 11, 21, ])
        )
        self.assertEqual(len(result), 1)

    def test_nin(self):
        """ Finds objects with the parameter not in the attribute."""
        result = self.Foo.find(
            Q('integer_field', 'nin', [1, 11, 21, ])
        )
        self.assertEqual(len(result), 2)


# TODO: MongoStorageTestCase not yet implemented
# class ComparisonOperatorsMongoTestCase(
#   ComparisonOperatorsBase,
#   MongoStorageTestCase
# ):
#     pass