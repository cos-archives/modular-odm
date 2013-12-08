import os

from modularodm import exceptions, fields, StoredObject
from modularodm.query.querydialect import DefaultQueryDialect as Q

from tests.base import ModularOdmTestCase


class UpdateQueryTestCase(ModularOdmTestCase):

    def define_objects(self):
        class Foo(StoredObject):
            _id = fields.IntegerField(primary=True)
            modified = fields.BooleanField(default=False)

        return Foo,

    def set_up_objects(self):
        self.foos = []

        for idx in xrange(5):
            foo = self.Foo(
                _id=idx
            )
            foo.save()
            self.foos.append(foo)

    def tear_down_objects(self):
        try:
            os.remove('db_Test.pkl')
        except OSError:
            pass

    def test_update(self):
        """ Given a query, and an update clause, update all (and only) object
        returned by query.
        """
        self.Foo.update(
            query=Q('_id', 'eq', 2),
            data={'modified': True}
        )

        self.assertEqual(
            [x.modified for x in self.foos],
            [False, False, True, False, False],
        )

    def test_update_one(self):
        """ Given a primary key, update the referenced object according to the
        update clause
        """
        self.Foo.update_one(
            which=Q('_id', 'eq', 2),
            data={'modified': True}
        )

        self.assertEqual(
            [x.modified for x in self.foos],
            [False, False, True, False, False],
        )

    def test_remove(self):
        """ Given a query, remove all (and only) object returned by query. """
        self.Foo.remove(Q('_id', 'eq', 2))

        self.assertEqual(
            self.Foo.find().count(),
            4
        )

    def test_remove_one(self):
        """ Given a primary key, remove the referenced object. """
        self.Foo.remove_one(Q('_id', 'eq', 2))

        self.assertEqual(
            self.Foo.find().count(),
            4
        )

    def test_remove_one_returns_many(self):
        """ Given a primary key, remove the referenced object. """
        with self.assertRaises(exceptions.ModularOdmException):
            self.Foo.remove_one(Q('_id', 'gt', 2))

    def test_remove_one_returns_none(self):
        """ Given a primary key, remove the referenced object. """
        with self.assertRaises(exceptions.ModularOdmException):
            self.Foo.remove_one(Q('_id', 'eq', 100))
