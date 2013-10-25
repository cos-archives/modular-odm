from modularodm.tests import ModularOdmTestCase, TestObject
from modularodm import fields


class OneToManyFieldTestCase(ModularOdmTestCase):

    def define_objects(self):

        class Foo(TestObject):
            _id = fields.IntegerField()
            title = fields.StringField()

        return Foo

    #def set_up_objects(self):
    #
    #    self.foo = self.Foo(_id=1)
    #    self.bar = self.Bar(_id=2)
    #
    #    self.bar.save()
    #
    #    self.foo.my_bar = self.bar
    #    self.foo.save()

    def test_save_diffs(self):
        pass

    def test_save_fulls(self):
        pass

    def test_load_diffs(self):
        pass

    def test_load_fulls(self):
        pass
