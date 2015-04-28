# -*- coding: utf-8 -*-
import os
import datetime
import unittest
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields, storage, exceptions


def set_datetime():
    return datetime.datetime(1999, 1, 2, 3, 45)


class User(StoredObject):
    _id = fields.StringField(primary=True)
    name = fields.StringField(required=True)
    date_created = fields.DateTimeField(auto_now_add=set_datetime)
    date_updated = fields.DateTimeField(auto_now=set_datetime)
    read_only = fields.StringField(editable=False)
    unique = fields.StringField(unique=True)

    _meta = {'optimistic': True}


pickle_storage = storage.PickleStorage('fields', prefix='test_')
User.set_storage(storage.PickleStorage('fields', prefix='test_'))


class TestField(unittest.TestCase):

    def setUp(self):
        pickle_storage._delete_file()

    def tearDown(self):
        pickle_storage._delete_file()

    def test_update_fields(self):
        u = User(name='foo')
        u.update_fields(name="bazzle", _id=932)
        assert_equal(u.name, "bazzle")
        assert_equal(u._id, 932)

    def test_validators_must_be_callable(self):
        assert_raises(TypeError, lambda: fields.Field(validate="invalid"))
        assert_raises(TypeError, lambda: fields.Field(validate=["invalid"]))

    def test_uneditable_field(self):
        u = User(name='Foo')
        with assert_raises(AttributeError):
            u.read_only = 'foo'

    def test_required_field(self):
        u = User()
        assert_raises(exceptions.ValidationError, lambda: u.save())

    def test_unique_field(self):
        u0 = User(name='bob', unique='foo')
        u1 = User(name='bob', unique='bar')
        u2 = User(name='bob', unique='foo')
        u0.save()
        u1.save()
        # Fail on saving repeated value
        with self.assertRaises(ValueError):
            u2.save()

    def test_unique_ignores_self(self):
        u0 = User(name='bob', unique='qux')
        u0.save()
        User._clear_caches()
        u0.save()

    def test_unique_ignores_none(self):
        u0 = User(name='bob')
        u1 = User(name='bob')
        u0.save()
        u1.save()


class TestListField(unittest.TestCase):

    def test_default_must_be_list(self):
        assert_raises(TypeError,
            lambda: fields.ListField(fields.StringField(), default=3))
        assert_raises(TypeError,
            lambda: fields.ListField(fields.StringField(), default="123"))
        assert_raises(TypeError,
            lambda: fields.ListField(fields.StringField(), default=True))
        assert_raises(TypeError,
            lambda: fields.ListField(fields.StringField(), default={"default": (1,2)}))


class TestDateTimeField(unittest.TestCase):

    def setUp(self):
        self.user = User(name="Foo")
        self.user.save()

    def tearDown(self):
        os.remove('test_fields.pkl')

    def test_auto_now_utcnow(self):
        expected = set_datetime()
        assert_equal(self.user.date_updated, expected)

    def test_auto_now_add(self):
        expected = set_datetime()
        assert_equal(self.user.date_created, expected)

    def test_uncallable_auto_now_param_raises_type_error(self):
        with assert_raises(ValueError):
            fields.DateTimeField(auto_now='uncallable')

    def test_cant_use_auto_now_and_auto_now_add(self):
        with assert_raises(ValueError):
            fields.DateTimeField(
                auto_now=datetime.datetime.now,
                auto_now_add=datetime.datetime.utcnow
            )


class TestForeignField(unittest.TestCase):

    def setUp(self):
        class Parent(StoredObject):
            _id = fields.IntegerField(primary=True)
        self.Parent = Parent

    def test_string_reference(self):
        class Child(StoredObject):
            _id = fields.IntegerField(primary=True)
            parent = fields.ForeignField('Parent')
        assert_equal(
            Child._fields['parent'].base_class,
            self.Parent
        )

    def test_string_reference_unknown(self):
        class Child(StoredObject):
            _id = fields.IntegerField(primary=True)
            parent = fields.ForeignField('Grandparent')
        with assert_raises(exceptions.ModularOdmException):
            Child._fields['parent'].base_class

    def test_class_reference(self):
        class Child(StoredObject):
            _id = fields.IntegerField(primary=True)
            parent = fields.ForeignField(self.Parent)
        assert_equal(
            Child._fields['parent'].base_class,
            self.Parent
        )


if __name__ == '__main__':
    unittest.main()
