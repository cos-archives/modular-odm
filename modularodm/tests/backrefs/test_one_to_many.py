from modularodm.tests import PickleStorageTestCase, TestObject

from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.ForeignField import ForeignField


class OneToManyFieldTestCase(PickleStorageTestCase):

    def setUp(self):

        class Foo(TestObject):
            _id = IntegerField()
            my_bar = ForeignField('Bar', backref='my_foo')

        class Bar(TestObject):
            _id = IntegerField()

        self.foo = Foo(_id=1)
        self.bar = Bar(_id=2)

        self.bar.save()

        self.foo.my_bar = self.bar
        self.foo.save()

        super(OneToManyFieldTestCase, self).setUp()

    def test_one_to_one_backref(self):

        # The object itself should be assigned
        self.assertIs(
            self.foo.my_bar,
            self.bar
        )

        # The backreference on bar should be a dict with the necessary info
        self.assertEqual(
            self.bar.my_foo,
            {'foo': {'my_bar': [self.foo._id]}}
        )

        # bar._backrefs should contain a dict with all backref information for
        # the object.
        self.assertEqual(
            self.bar._backrefs,
            {'my_foo': {'foo': {'my_bar': [self.foo._id]}}}
        )

    def test_delete_foreign_field(self):
        """ Remove an element from a ForeignField, and verify that it was
        removed from the backref as well.
        """

        del self.foo.my_bar
        self.foo.save()

        # The first Bar should be gone from the ForeignField
        self.assertEqual(
            self.foo.my_bar,
            None,
        )

        # The first Bar should no longer have a reference to foo
        self.assertEqual(
            self.bar.my_foo,
            {'foo': {'my_bar': []}}
        )

    def test_assign_foreign_field_to_none(self):
        """ Assigning a ForeignField to None should be have the same effect as
        deleting it.
        """

        #
        self.foo.my_bar = None
        self.foo.save()

        # The first Bar should be gone from the ForeignField
        self.assertEqual(
            self.foo.my_bar,
            None,
        )

        # The first Bar should no longer have a reference to foo
        self.assertEqual(
            self.bar.my_foo,
            {'foo': {'my_bar': []}}
        )

    def test_assign_foreign_field_by_id(self):
        """ Try assigning a ForeignField to the primary key of a remote object
        """

        # this functionality is not yet defined.
        self.foo.my_bar = self.bar._id