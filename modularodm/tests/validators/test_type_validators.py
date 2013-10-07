import datetime as dt

from modularodm import StoredObject
from modularodm.exceptions import ValidationTypeError
from modularodm.fields import (
    BooleanField,
    DateTimeField,
    FloatField,
    IntegerField,
    StringField,
)
from modularodm.tests import ModularOdmTestCase


class BooleanValidatorTestCase(ModularOdmTestCase):
    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            field = BooleanField(list=False, validate=True)

        self.test_object = Foo()
        return Foo,

    def test_bool(self):

        self.test_object.field = True
        self.test_object.save()

    def test_datetime(self):
        self.test_object.field = dt.datetime.now()
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_integer(self):

        self.test_object.field = 1
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_float(self):

        self.test_object.field = 42.1
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_string(self):

        self.test_object.field = 'I am a string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_unicode(self):

        self.test_object.field = u'I am a unicode string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()


class DateTimeValidatorTestCase(ModularOdmTestCase):
    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            field = DateTimeField(list=False, validate=True)

        self.test_object = Foo()

        return Foo,

    def test_bool(self):

        self.test_object.field = True
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_datetime(self):
        self.test_object.field = dt.datetime.now()
        self.test_object.save()

    def test_integer(self):

        self.test_object.field = 42
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_float(self):

        self.test_object.field = 42.1
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_string(self):

        self.test_object.field = 'I am a string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_unicode(self):

        self.test_object.field = u'I am a unicode string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()


class FloatValidatorTestCase(ModularOdmTestCase):
    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            field = FloatField(list=False, validate=True)

        self.test_object = Foo()

        return Foo,

    def test_bool(self):

        self.test_object.field = True
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_datetime(self):
        self.test_object.field = dt.datetime.now()
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_integer(self):

        self.test_object.field = 42
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_float(self):

        self.test_object.field = 42.1
        self.test_object.save()

    def test_string(self):

        self.test_object.field = 'I am a string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_unicode(self):

        self.test_object.field = u'I am a unicode string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()


class IntegerValidatorTestCase(ModularOdmTestCase):
    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            field = IntegerField(list=False, validate=True)

        self.test_object = Foo()

        return Foo,

    def test_bool(self):

        self.test_object.field = True
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_datetime(self):
        self.test_object.field = dt.datetime.now()
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_integer(self):

        self.test_object.field = 42
        self.test_object.save()

    def test_float(self):

        self.test_object.field = 42.1
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_string(self):

        self.test_object.field = 'I am a string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_unicode(self):

        self.test_object.field = u'I am a unicode string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()


class StringValidatorTestCase(ModularOdmTestCase):
    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            field = StringField(list=False, validate=True)

        self.test_object = Foo()

        return Foo,

    def test_bool(self):

        self.test_object.field = True
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_datetime(self):
        self.test_object.field = dt.datetime.now()
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_integer(self):

        self.test_object.field = 42
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_float(self):

        self.test_object.field = 42.1
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_string(self):

        self.test_object.field = 'I am a string'
        self.test_object.save()

    def test_unicode(self):

        self.test_object.field = u'I am a unicode string'
        self.test_object.save()


class ListValidatorTestCase(ModularOdmTestCase):
    def define_objects(self):
        class Foo(StoredObject):
            _id = IntegerField()
            field = StringField(list=True, validate=True)

        self.test_object = Foo()

        return Foo,

    def test_bool(self):

        self.test_object.field = [True, False]
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_datetime(self):
        self.test_object.field = [dt.datetime.now(), dt.datetime.now()]
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_integer(self):

        self.test_object.field = [42, 43, 44]
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_float(self):

        self.test_object.field = [42.1, 43.1]
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_string(self):

        self.test_object.field = 'I am a string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_list_of_strings(self):

        self.test_object.field = ['I am a string', 'so am I']
        self.test_object.save()

    def test_unicode(self):

        self.test_object.field = u'I am a unicode string'
        with self.assertRaises(ValidationTypeError):
            self.test_object.save()

    def test_list_of_unicodes(self):

        self.test_object.field = [u'I am a unicode string', u'I am too..']
        self.test_object.save()