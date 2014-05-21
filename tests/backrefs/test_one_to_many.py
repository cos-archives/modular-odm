# -*- coding: utf-8 -*-

from nose.tools import *

from modularodm import fields

from tests.base import ModularOdmTestCase, TestObject


class OneToManyFieldTestCase(ModularOdmTestCase):

    def define_objects(self):

        class Foo(TestObject):
            _id = fields.IntegerField()
            my_bar = fields.ForeignField('Bar', backref='my_foo')
            my_bar_no_backref = fields.ForeignField('Bar')

        class Bar(TestObject):
            _id = fields.IntegerField()

        return Foo, Bar

    def set_up_objects(self):

        self.foo = self.Foo(_id=1)
        self.bar = self.Bar(_id=2)

        self.bar.save()

        self.foo.my_bar = self.bar
        self.foo.save()

    def test_no_backref(self):
        """Regression test; ensure that backrefs are not saved when no backref
        key is given.
        """
        bar = self.Bar(_id=20)
        bar.save()

        self.foo.my_bar_no_backref = bar
        self.foo.save()

        assert_equal(bar._backrefs, {})

    def test_one_to_one_backref(self):

        # The object itself should be assigned
        self.assertIs(
            self.foo.my_bar,
            self.bar
        )

        # The backreference on bar should be a dict with the necessary info
        self.assertEqual(
            self.bar.my_foo[0],
            self.foo
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
            []
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
            []
        )

    def test_assign_foreign_field_by_id(self):
        """ Try assigning a ForeignField to the primary key of a remote object
        """

        # this functionality is not yet defined.
        self.foo.my_bar = self.bar._id
        self.assertIs(
            self.foo.my_bar,
            self.bar
        )


class OneToManyAbstractFieldTestCase(ModularOdmTestCase):

    def define_objects(self):

        class Foo(TestObject):
            _id = fields.IntegerField()
            my_abstract = fields.AbstractForeignField(backref='my_foo')

        class Bar(TestObject):
            _id = fields.IntegerField()

        class Bob(TestObject):
            _id = fields.IntegerField()

        return Foo, Bar, Bob

    def set_up_objects(self):

        self.bar = self.Bar(_id=3)
        self.bob = self.Bar(_id=4)

        self.bar.save()
        self.bob.save()

        self.foo1 = self.Foo(_id=1, my_abstract=self.bar)
        self.foo1.save()

        self.foo2 = self.Foo(_id=2, my_abstract=self.bob)
        self.foo2.save()

    def test_one_to_one_backref(self):

        # The object itself should be assigned
        self.assertIs(
            self.foo1.my_abstract,
            self.bar
        )
        self.assertIs(
            self.foo2.my_abstract,
            self.bob
        )

        # The backreference on bar should be a dict with the necessary info
        self.assertEqual(
            self.bar.my_foo[0],
            self.foo1
        )
        self.assertEqual(
            self.bob.my_foo[0],
            self.foo2
        )

        # bar._backrefs should contain a dict with all backref information for
        # the object.
        self.assertEqual(
            self.bar._backrefs,
            {'my_foo': {'foo': {'my_abstract': [self.foo1._id]}}}
        )
        self.assertEqual(
            self.bob._backrefs,
            {'my_foo': {'foo': {'my_abstract': [self.foo2._id]}}}
        )

    def test_delete_foreign_field(self):
        """ Remove an element from a ForeignField, and verify that it was
        removed from the backref as well.
        """

        del self.foo1.my_abstract
        self.foo1.save()
        del self.foo2.my_abstract
        self.foo2.save()

        # The first Bar should be gone from the ForeignField
        self.assertEqual(
            self.foo1.my_abstract,
            None,
        )
        self.assertEqual(
            self.foo2.my_abstract,
            None,
        )

        # The first Bar should no longer have a reference to foo
        self.assertEqual(
            self.bar.my_foo,
            []
        )
        self.assertEqual(
            self.bob.my_foo,
            []
        )

    def test_assign_foreign_field_to_none(self):
        """ Assigning a ForeignField to None should be have the same effect as
        deleting it.
        """

        #
        self.foo1.my_abstract = None
        self.foo1.save()
        self.foo2.my_abstract = None
        self.foo2.save()

        # The first Bar should be gone from the ForeignField
        self.assertEqual(
            self.foo1.my_abstract,
            None,
        )
        self.assertEqual(
            self.foo2.my_abstract,
            None,
        )

        # The first Bar should no longer have a reference to foo
        self.assertEqual(
            self.bar.my_foo,
            []
        )
        self.assertEqual(
            self.bob.my_foo,
            []
        )

    def test_assign_foreign_field_by_tuple(self):
        """Assign a tuple of a primary key and a schema name to an abstract
        foreign field. Verify that the value of the abstract foreign field is
        the same as the object whose primary key and schema name passed in.

        """
        self.foo1.my_abstract = (self.bar._id, self.bar._name)

        self.assertIs(
            self.foo1.my_abstract,
            self.bar
        )

    def test_assign_foreign_field_invalid_type(self):
        """Try to assign a value of the wrong type to an abstract foreign
        field; should raise a TypeError.

        """
        with self.assertRaises(TypeError):
            self.foo1.my_abstract = 'some primary key'

    def test_assign_foreign_field_invalid_length(self):
        """Try to assign a tuple of the wrong length to an abstract foreign
        field; should raise a ValueError.

        """
        with self.assertRaises(ValueError):
            self.foo1.my_abstract = ('tuple', 'of', 'wrong', 'length')
