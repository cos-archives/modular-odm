from modularodm.exceptions import ValidationValueError
from modularodm.tests import TestObject, PickleStorageTestCase

from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.FloatField import FloatField

from modularodm.validators import MinValueValidator, MaxValueValidator


class ValueValidatorTestCase(PickleStorageTestCase):

    def test_min_value_int_validator(self):

        class Foo(TestObject):
            _id = IntegerField()
            int_field = IntegerField(
                list=False,
                validate=[MinValueValidator(5), ]
            )

        test_object = Foo()
        test_object.int_field = 10
        test_object.save()

        test_object.int_field = 0
        with self.assertRaises(ValidationValueError):
            test_object.save()

    def test_max_value_int_validator(self):

        class Foo(TestObject):
            _id = IntegerField()
            int_field = IntegerField(
                list=False,
                validate=[MaxValueValidator(5), ]
            )

        test_object = Foo()
        test_object.int_field = 0
        test_object.save()

        test_object.int_field = 10
        with self.assertRaises(ValidationValueError):
            test_object.save()

    def test_min_value_float_validator(self):

        class Foo(TestObject):
            _id = IntegerField()
            float_field = FloatField(
                list=False,
                validate=[MinValueValidator(5.), ]
            )

        test_object = Foo()
        test_object.float_field = 10.
        test_object.save()

        test_object.float_field = 0.
        with self.assertRaises(ValidationValueError):
            test_object.save()

    def test_max_value_float_validator(self):

        class Foo(TestObject):
            _id = IntegerField()
            float_field = FloatField(
                list=False,
                validate=[MaxValueValidator(5.), ]
            )

        test_object = Foo()
        test_object.float_field = 0.
        test_object.save()

        test_object.float_field = 10.
        with self.assertRaises(ValidationValueError):
            test_object.save()