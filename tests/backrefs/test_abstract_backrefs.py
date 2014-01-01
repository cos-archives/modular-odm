
from modularodm import fields

from tests.base import ModularOdmTestCase, TestObject

class OneToManyFieldTestCase(ModularOdmTestCase):

    def define_objects(self):

        class Foo(TestObject):
            _id = fields.IntegerField()

        class Bar(TestObject):
            _id = fields.IntegerField()
            ref = fields.ForeignField('foo', backref='food')

        class Baz(TestObject):
            _id = fields.IntegerField()
            ref = fields.ForeignField('foo', backref='food')

        return Foo, Bar, Baz

    def set_up_objects(self):

        self.foo = self.Foo(_id=1)
        self.foo.save()

        self.bar = self.Bar(_id=2, ref=self.foo)
        self.baz = self.Bar(_id=3, ref=self.foo)

        self.bar.save()
        self.baz.save()

    def test_abstract_backrefs(self):

        backrefs = self.foo.food
        self.assertIn(self.bar, backrefs)
        self.assertIn(self.baz, backrefs)
