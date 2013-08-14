from modularodm.tests import PickleStorageTestCase, TestObject

from modularodm import exceptions as exc
from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.ForeignField import ForeignField


class ManyToManyFieldTestCase(PickleStorageTestCase):

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

        super(ManyToManyFieldTestCase, self).setUp()

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

    def test_contains(self):
        """ Verify that the "in" operator works as expected """

        self.assertIn(
            self.bar,
            self.foo.my_bar
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

    def test_insert(self):
        """ Add a new object to the middle of a ForeignList field via .insert()
        """

        # create a new bar
        new_bar = self.Bar(_id=9)
        new_bar.save()

        # insert new_bar into foo's .my_bar
        self.foo.my_bar.insert(1, new_bar)
        self.foo.save()

        # new_bar should now be in the list
        self.assertIn(
            new_bar,
            self.foo.my_bar,
        )

        # new_bar should have a backref to foo
        self.assertEqual(
            new_bar.my_foo,
            {'foo': {'my_bar': [1]}},
        )

    def test_replace_backref(self):
        """ Replace an existing item in the ForeignList field with another
         remote object.
        """

        # create a new bar
        new_bar = self.Bar(_id=9)
        new_bar.save()

        # replace the first bar in the list with it.
        old_bar_id = self.foo.my_bar[0]._id
        self.foo.my_bar[0] = new_bar
        self.foo.save()

        # the old Bar should no longer have a backref to foo
        old_bar = self.Bar.load(old_bar_id)
        self.assertEqual(
            old_bar._backrefs,
            {'my_foo': {'foo': {'my_bar': []}}}
        )

        # the new Bar should have a backref to foo
        self.assertEqual(
            new_bar._backrefs,
            {'my_foo': {'foo': {'my_bar': [1]}}}
        )
        print new_bar._backrefs

    def test_delete_backref_attribute_from_remote_via_pop(self):
        """ Delete a backref from its attribute on the remote object by calling
        .pop().

        Backref attributes on the remote object should be read-only.
        """

        with self.assertRaises(exc.ModularOdmException):
            self.bar.my_foo['foo']['my_bar'].pop()

    def test_delete_backref_attribute_from_remote_via_del(self):
        """ Delete a backref from its attribute from the remote object directly.

        Backref attributes on the remote object should be read-only.
        """

        with self.assertRaises(exc.ModularOdmException):
            del self.bar.my_foo['foo']['my_bar'][0]

    def test_assign_backref_attribute_from_remote(self):
        """ Manually assign a backref to its attribute on the remote object.

         Backref attributes on the remote object should be read-only.
        """

        with self.assertRaises(exc.ModularOdmException):
            self.bar.my_foo = {'foo': {'my_bar': []}}

    def test_del_key_from_backrefs_on_remote(self):
        """ Manually remove a key from _backrefs on the remote object.

        _backrefs on the remote object should be read-only.
        """
        with self.assertRaises(exc.ModularOdmException):
            del self.bar._backrefs['my_foo']

    def test_assign_backrefs_on_remote(self):
        """ Manually assign a backref on the remote object directly.

        _backrefs on the remote object should be read-only.
        """
        with self.assertRaises(exc.ModularOdmException):
            self.bar._backrefs = {'my_foo': {'foo': {'my_bar': [self.foo._id]}}}