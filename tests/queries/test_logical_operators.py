from modularodm import fields, StoredObject
from modularodm.query.querydialect import DefaultQueryDialect as Q

from tests import ModularOdmTestCase

class LogicalOperatorsBase(ModularOdmTestCase):
    def define_objects(self):
        class Foo(StoredObject):
            _id = fields.IntegerField(required=True, primary=True)
            a = fields.IntegerField()
            b = fields.IntegerField()

        return Foo,

    def set_up_objects(self):
        self.foos =  []

        for idx, f in  enumerate([(a, b) for a in xrange(3) for b in xrange(3)]):
            self.foos.append(
                self.Foo(
                    _id = idx,
                    a = f[0],
                    b = f[1],
                )
            )

        [x.save() for x in self.foos]

    def test_and(self):
        """ Finds the intersection of two or more queries."""
        result = self.Foo.find(Q('a', 'eq', 0) & Q('b', 'eq', 1))
        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(result[0].a, 0)
        self.assertEqual(result[0].b, 1)

    def test_or(self):
        """ Finds the union of two or more queries."""
        result = self.Foo.find(Q('a', 'eq', 0) | Q('a', 'eq', 1))
        self.assertEqual(
            len(result),
            6,
        )

    def test_not(self):
        """ Finds the inverse of a query."""

        # This is failing in Mongo, but works in Pickle. Mongo is getting:
        #       {'$not': {'a': 0}}
        # but it should be getting
        #       {'a': {'$not': 0}}
        #
        # See: http://docs.mongodb.org/manual/reference/operator/not/
        result = self.Foo.find(~Q('a', 'eq', 0))
        self.assertEqual(
            len(result),
            6,
        )
