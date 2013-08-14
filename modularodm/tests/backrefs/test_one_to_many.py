from modularodm.tests import PickleStorageTestCase, TestObject

from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.ForeignField import ForeignField


class Foo(TestObject):
    _id = IntegerField()
    my_bar = ForeignField('Bar', backref='my_foo')


class Bar(TestObject):
    _id = IntegerField()


class OneToOneFieldTestCase(PickleStorageTestCase):

    def test_simple_backref(self):
        foo = Foo(_id=1)
        bar = Bar(_id=2)

        bar.save()

        foo.my_bar = bar
        foo.save()

        # The object itself should be assigned
        self.assertIs(
            foo.my_bar,
            bar
        )

        # The backreference on bar should be a dict with the necessary info
        self.assertEqual(
            bar.my_foo,
            {'foo': {'my_bar': [foo._id]}}
        )

        # bar._backrefs should contain a dict with all backref information for
        # the object.
        self.assertEqual(
            bar._backrefs,
            {'my_foo': {'foo': {'my_bar': [foo._id]}}}
        )