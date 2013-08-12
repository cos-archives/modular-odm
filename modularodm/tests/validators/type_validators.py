import datetime as dt

from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.StringField import StringField
from modularodm.fields.BooleanField import BooleanField
from modularodm.fields.FloatField import FloatField
from modularodm.fields.DateTimeField import DateTimeField

from modularodm.tests.validators import TestObject, PickleStorageTestCase

from modularodm.validators import ValidationTypeError


class BooleanValidatorTestCase(PickleStorageTestCase):
    def setUp(self):
        class Foo(TestObject):
            _id = IntegerField()
            field = BooleanField(list=False, validate=True)

        self.test_object = Foo()

        super(BooleanValidatorTestCase, self).setUp()

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


class DateTimeValidatorTestCase(PickleStorageTestCase):
    def setUp(self):
        class Foo(TestObject):
            _id = IntegerField()
            field = DateTimeField(list=False, validate=True)

        self.test_object = Foo()

        super(DateTimeValidatorTestCase, self).setUp()

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


class FloatValidatorTestCase(PickleStorageTestCase):
    def setUp(self):
        class Foo(TestObject):
            _id = IntegerField()
            field = FloatField(list=False, validate=True)

        self.test_object = Foo()

        super(FloatValidatorTestCase, self).setUp()

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


class IntegerValidatorTestCase(PickleStorageTestCase):
    def setUp(self):
        class Foo(TestObject):
            _id = IntegerField()
            field = IntegerField(list=False, validate=True)

        self.test_object = Foo()

        super(IntegerValidatorTestCase, self).setUp()

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


class StringValidatorTestCase(PickleStorageTestCase):
    def setUp(self):
        class Foo(TestObject):
            _id = IntegerField()
            field = StringField(list=False, validate=True)

        self.test_object = Foo()

        super(StringValidatorTestCase, self).setUp()

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


class ListValidatorTestCase(PickleStorageTestCase):
    def setUp(self):
        class Foo(TestObject):
            _id = IntegerField()
            field = StringField(list=True, validate=True)

        self.test_object = Foo()

        super(ListValidatorTestCase, self).setUp()

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