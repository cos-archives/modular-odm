from modularodm import StoredObject
from modularodm.exceptions import ValidationValueError
from modularodm.fields import FloatField, IntegerField
from modularodm.validators import MinValueValidator, MaxValueValidator

from tests import ModularOdmTestCase

class IntValueValidatorTestCase(ModularOdmTestCase):

    def test_min_value_int_validator(self):

        class Foo(StoredObject):
            _id = IntegerField()
            int_field = IntegerField(
                list=False,
                validate=[MinValueValidator(5), ]
            )
        Foo.set_storage(self.make_storage())

        test_object = Foo()
        test_object.int_field = 10
        test_object.save()

        test_object.int_field = 0
        with self.assertRaises(ValidationValueError):
            test_object.save()

    def test_max_value_int_validator(self):

        class Foo(StoredObject):
            _id = IntegerField()
            int_field = IntegerField(
                list=False,
                validate=[MaxValueValidator(5), ]
            )
        Foo.set_storage(self.make_storage())

        test_object = Foo()
        test_object.int_field = 0
        test_object.save()

        test_object.int_field = 10
        with self.assertRaises(ValidationValueError):
            test_object.save()

    def test_min_value_float_validator(self):

        class Foo(StoredObject):
            _id = IntegerField()
            float_field = FloatField(
                list=False,
                validate=[MinValueValidator(5.), ]
            )
        Foo.set_storage(self.make_storage())

        test_object = Foo()
        test_object.float_field = 10.
        test_object.save()

        test_object.float_field = 0.
        with self.assertRaises(ValidationValueError):
            test_object.save()

    def test_max_value_float_validator(self):

        class Foo(StoredObject):
            _id = IntegerField()
            float_field = FloatField(
                list=False,
                validate=[MaxValueValidator(5.), ]
            )
        Foo.set_storage(self.make_storage())

        test_object = Foo()
        test_object.float_field = 0.
        test_object.save()

        test_object.float_field = 10.
        with self.assertRaises(ValidationValueError):
            test_object.save()
