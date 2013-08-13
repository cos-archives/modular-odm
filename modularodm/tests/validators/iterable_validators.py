from modularodm.tests.validators import TestObject, PickleStorageTestCase

from modularodm.fields.StringField import StringField
from modularodm.fields.IntegerField import IntegerField

from modularodm.validators.exceptions import (
    ValidationValueError,
    ValidationTypeError,
)

from modularodm.validators import MaxLengthValidator, MinLengthValidator


class IterableValidatorTestCase(PickleStorageTestCase):

    def test_max_length_string_validator(self):
        class Foo(TestObject):
            _id = IntegerField()
            test_field = StringField(
                list=False,
                validate=[MaxLengthValidator(5), ]
            )
        obj = Foo()

        obj.test_field = 'abc'
        obj.save()

        obj.test_field = 'abcdefg'
        with self.assertRaises(ValidationValueError):
            obj.save()

    def test_min_length_string_validator(self):
        class Foo(TestObject):
            _id = IntegerField()
            test_field = StringField(
                list=False,
                validate=[MinLengthValidator(5), ]
            )
        obj = Foo()

        obj.test_field = 'abc'
        with self.assertRaises(ValidationValueError):
            obj.save()

        obj.test_field = 'abcdefg'
        obj.save()

    def test_min_length_list_validator(self):
        # This test fails.
        class Foo(TestObject):
            _id = IntegerField()
            test_field = IntegerField(
                list=True,
                list_validate=[MinLengthValidator(5), ]
            )
        obj = Foo()

        obj.test_field = [1, 2, 3]
        with self.assertRaises(ValidationValueError):
            obj.save()

        obj.test_field = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        obj.save()

    def test_max_length_list_validator(self):
        # This test fails.
        class Foo(TestObject):
            _id = IntegerField()
            test_field = IntegerField(
                list=True,
                list_validate=[MaxLengthValidator(5), ]
            )
        obj = Foo()

        obj.test_field = [1, 2, 3]
        obj.save()

        obj.test_field = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        with self.assertRaises(ValidationValueError):
            obj.save()


class IterableValidatorCombinationTestCase(PickleStorageTestCase):
    def setUp(self):
        class Foo(TestObject):
            _id = IntegerField()
            test_field = StringField(
                list=True,
                validate=MaxLengthValidator(3),
                list_validate=MinLengthValidator(3)
            )
        self.test_object = Foo()

    def test_child_pass_list_fail(self):
        self.test_object.test_field = ['ab', 'abc']

        with self.assertRaises(ValidationValueError):
            self.test_object.save()

    def test_child_fail_list_pass(self):
        self.test_object.test_field = ['ab', 'abcd', 'adc']

        with self.assertRaises(ValidationValueError):
            self.test_object.save()

    def test_child_fail_list_fail(self):
        self.test_object.test_field = ['ab', 'abdc']

        with self.assertRaises(ValidationValueError):
            self.test_object.save()

