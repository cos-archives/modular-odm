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

        # Assign classes ot the test fixture
        self.Foo = Foo
        self.Bar = Bar

        # create a Foo and two Bars
        self.foo = Foo(_id=1)
        self.bar = Bar(_id=2)
        self.baz = Bar(_id=3)

        # save the bars so they're in the storage
        self.bar.save()
        self.baz.save()

        # add the bars to the foo
        self.foo.my_bar.append(self.bar)
        self.foo.my_bar.append(self.baz)

        # save foo to persist changes
        self.foo.save()

        super(OneToManyFieldTestCase, self).setUp()

    def test_one_to_many_backref(self):

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

    def test_delete_backref(self):
        """ Remove an element from a ForeignField, and verify that it was
        removed from the backref as well.
        """

        first_bar = self.foo.my_bar[0]
        second_bar = self.foo.my_bar[1]

        del self.foo.my_bar[0]
        self.foo.save()

        # The first Bar should be gone from the ForeignField
        self.assertEqual(
            list(self.foo.my_bar),
            [second_bar, ],
        )

        # The first Bar should no longer have a reference to foo
        self.assertEqual(
            first_bar.my_foo,
            {'foo': {'my_bar': []}}
        )