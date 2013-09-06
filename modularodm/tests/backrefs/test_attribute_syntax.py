import unittest

from modularodm.fields import ForeignField, StringField, ForeignList
from modularodm.tests import ModularOdmTestCase, TestObject



class OneToManyFieldTestCase(ModularOdmTestCase):

    def define_test_objects(self):

        class Foo(TestObject):
            _meta = {
                'optimistic': True
            }
            _id = StringField()
            my_bar = ForeignField('Bar', backref='my_foos')
            my_other_bar = ForeignField('Bar', backref='my_foos')

        class Bar(TestObject):
            _meta = {'optimistic': True}
            _id = StringField()

        return Foo, Bar

    def set_up_test_objects(self):

        self.bar = self.Bar()
        self.bar.save()

        self.foos = []
        for i in xrange(5):
            foo = self.Foo()
            if i > 0:
                foo.my_bar = self.bar
            else:
                foo.my_other_bar = self.bar
            foo.save()
            self.foos.append(foo)

    def test_dunder_br_returns_foreignlist(self):
        self.assertIs(
            type(self.bar.foo__my_foos),
            ForeignList
        )

    def test_dunder_br_returns_correct(self):
        self.assertEqual(
            len(self.bar.foo__my_foos),
            5
        )

    @unittest.skip('Behavior not defined.')
    def test_dunder_br_unknown_field(self):
        with self.assertRaises(KeyError):
            self.bar.foo__not_a_real_key

    def test_dunder_br_unknown_node(self):
        with self.assertRaises(KeyError):
            self.bar.not_a_real_node__foo

    def test_dunder_br_parent_field_correct(self):
        self.assertEqual(
            len(self.bar.foo__my_foos__my_other_bar),
            1
        )