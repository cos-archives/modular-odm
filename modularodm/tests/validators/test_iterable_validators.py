from modularodm import StoredObject
from modularodm.exceptions import ValidationValueError
from modularodm.fields import IntegerField, StringField
from modularodm.tests import ModularOdmTestCase
from modularodm.validators import MaxLengthValidator, MinLengthValidator


class StringValidatorTestCase(ModularOdmTestCase):

    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            test_field_max = StringField(
                list=False,
                validate=[MaxLengthValidator(5), ]
            )
            test_field_min = StringField(
                list=False,
                validate=[MinLengthValidator(5), ]
            )
        self.test_object = Foo(_id=0)
        return Foo,

    def test_max_length_string_validator(self):
        
        self.test_object.test_field_max = 'abc'
        self.test_object.save()

        self.test_object.test_field_max = 'abcdefg'
        with self.assertRaises(ValidationValueError):
            self.test_object.save()

    def test_min_length_string_validator(self):

        self.test_object.test_field_min = 'abc'
        with self.assertRaises(ValidationValueError):
            self.test_object.save()

        self.test_object.test_field_min = 'abcdefg'
        self.test_object.save()


class ListValidatorTestCase(ModularOdmTestCase):

    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            test_field_max = IntegerField(
                list=True,
                list_validate=[MaxLengthValidator(5), ]
            )
            test_field_min = IntegerField(
                list=True,
                list_validate=[MinLengthValidator(3), ]
            )
        self.test_object = Foo(_id=0)
        return Foo,

    def test_min_length_list_validator(self):
        # This test fails.

        self.test_object.test_field_min = [1, 2]
        with self.assertRaises(ValidationValueError):
            self.test_object.save()

        self.test_object.test_field_min = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        self.test_object.save()

    def test_max_length_list_validator(self):
        # This test fails.

        self.test_object.test_field_min = [1, 2, 3]
        self.test_object.test_field_max = [1, 2, 3]
        self.test_object.save()

        self.test_object.test_field_max = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        with self.assertRaises(ValidationValueError):
            self.test_object.save()


class IterableValidatorCombinationTestCase(ModularOdmTestCase):
    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            test_field = StringField(
                list=True,
                validate=MaxLengthValidator(3),
                list_validate=MinLengthValidator(3)
            )
        self.test_object = Foo(_id=0)
        return Foo,

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

