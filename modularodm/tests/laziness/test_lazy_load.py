from modularodm.tests import ModularOdmTestCase

from modularodm import StoredObject
from modularodm.storedobject import ContextLogger
from modularodm.fields import ForeignField, IntegerField

class LazyLoadTestCase(ModularOdmTestCase):

    def define_test_objects(self):

        class Foo(StoredObject):
            _id = IntegerField()
            my_bar = ForeignField('Bar', list=True, backref='my_foo')

        class Bar(StoredObject):
            _id = IntegerField()

        return Foo, Bar

    def test_create_one_object(self):

        with ContextLogger() as context_logger:

            bar = self.Bar(_id=1)
            bar.save()

            report = context_logger.report()

        self.assertEqual(report[('bar', 'insert')][0], 1)

    def test_load_object_in_cache(self):

        bar = self.Bar(_id=1)
        bar.save()

        with ContextLogger() as context_logger:

            self.Bar.load(1)
            report = context_logger.report()

        self.assertNotIn(('bar', 'load'), report)

    def test_load_object_not_in_cache(self):

        bar = self.Bar(_id=1)
        bar.save()

        self.Bar._clear_caches(1)

        with ContextLogger() as context_logger:

            self.Bar.load(1)
            report = context_logger.report()

        self.assertEqual(report[('bar', 'get')][0], 1)

    def test_create_several_objects(self):

        with ContextLogger() as context_logger:

            bar1 = self.Bar(_id=1)
            bar2 = self.Bar(_id=2)
            bar3 = self.Bar(_id=3)
            bar4 = self.Bar(_id=4)
            bar5 = self.Bar(_id=5)

            bar1.save()
            bar2.save()
            bar3.save()
            bar4.save()
            bar5.save()

            report = context_logger.report()

        self.assertEqual(report[('bar', 'insert')][0], 5)

    def test_create_linked_objects(self):

        bar1 = self.Bar(_id=1)
        bar2 = self.Bar(_id=2)
        bar3 = self.Bar(_id=3)

        bar1.save()
        bar2.save()
        bar3.save()

        with ContextLogger() as context_logger:

            foo1 = self.Foo(_id=4)
            foo1.my_bar = [bar1, bar2, bar3]
            foo1.save()

            report = context_logger.report()

        self.assertEqual(report[('foo', 'insert')][0], 1)
        self.assertEqual(report[('bar', 'update')][0], 3)

    def test_load_linked_objects_not_in_cache(self):

        bar1 = self.Bar(_id=1)
        bar2 = self.Bar(_id=2)
        bar3 = self.Bar(_id=3)

        bar1.save()
        bar2.save()
        bar3.save()

        foo1 = self.Foo(_id=4)
        foo1.my_bar = [bar1, bar2, bar3]
        foo1.save()

        StoredObject._clear_caches()

        with ContextLogger() as context_logger:

            self.Foo.load(4)

            report = context_logger.report()

        self.assertEqual(report[('foo', 'get')][0], 1)
        self.assertNotIn(('bar', 'get'), report)
