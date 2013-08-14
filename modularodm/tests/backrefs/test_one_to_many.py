from modularodm.tests import PickleStorageTestCase, TestObject

from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.ForeignField import ForeignField


class OneToManyFieldTestCase(PickleStorageTestCase):

    def setUp(self):
        class Foo(TestObject):
            _id = IntegerField()
            my_bar = ForeignField('Bar', list=True, backref='my_foo')

        class Bar(TestObject):
            _id = IntegerField()

        self.foo = Foo(_id=1)
        self.bar = Bar(_id=2)
        self.baz = Bar(_id=3)

        self.bar.save()
        self.baz.save()

        self.foo.my_bar.append(self.bar)
        self.foo.my_bar.append(self.baz)
        self.foo.save()

        super(OneToManyFieldTestCase, self).setUp()

    def test_simple_backref(self):

        # Should be a list of the object's ID
        # TODO: Shouldn't this be the objects themselves? Why not?

        self.assertEqual(
            list(self.foo.my_bar),
            [self.bar, self.baz]
        )

        # The backreference on bar should be a dict with the necessary info
        self.assertEqual(
            self.bar.my_foo,
            {'foo': {'my_bar': [self.foo._id]}}
        )

        # The backreference on baz should be the same
        self.assertEqual(
            self.baz.my_foo,
            {'foo': {'my_bar': [self.foo._id]}}
        )

        # bar._backrefs should contain a dict with all backref information for
        # the object.
        self.assertEqual(
            self.bar._backrefs,
            {'my_foo': {'foo': {'my_bar': [self.foo._id]}}}
        )

        # bar._backrefs should contain a dict with all backref information for
        # the object.
        self.assertEqual(
            self.baz._backrefs,
            {'my_foo': {'foo': {'my_bar': [self.foo._id]}}}
        )