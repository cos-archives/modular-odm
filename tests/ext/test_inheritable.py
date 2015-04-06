from nose.tools import *

from modularodm import fields, Q
from modularodm.ext.inheritable import InheritableStoredObject
from tests.base import ModularOdmTestCase


class InheritableStoredObjectTestCase(ModularOdmTestCase):
    def define_objects(self):
        class Top(InheritableStoredObject):
            _meta = {'optimistic':True}

            _id = fields.IntegerField(primary=True)

        class Middle(Top):
            pass

        class Bottom(Middle):
            pass

        return Top, Middle, Bottom

    def set_up_objects(self):
        self.top = self.Top(_id=0)
        self.top.save()

        self.middle = self.Middle(_id=1)
        self.middle.save()

        self.bottom = self.Bottom(_id=2)
        self.bottom.save()

    def test_find(self):
        # correct number of instances
        assert_equal(self.Top.find().count(), 3)
        assert_equal(self.Middle.find().count(), 2)
        assert_equal(self.Bottom.find().count(), 1)

        # correct objects
        assert_equal(
            set([each._id for each in self.Top.find()]),
            {0, 1, 2},
        )
        assert_equal(
            set([each._id for each in self.Middle.find()]),
            {1, 2},
        )
        assert_equal(
            set([each._id for each in self.Bottom.find()]),
            {2},
        )

        # correct classes
        assert_equal(
            set([each.__class__ for each in self.Top.find()]),
            {self.Top, self.Middle, self.Bottom},
        )
        assert_equal(
            set([each.__class__ for each in self.Middle.find()]),
            {self.Middle, self.Bottom},
        )
        assert_equal(
            set([each.__class__ for each in self.Bottom.find()]),
            {self.Bottom},
        )

    def test_find_one(self):
        instance = self.Top.find_one(Q('_id', 'eq', 2))

        # correct class
        assert_equal(
            instance.__class__,
            self.Bottom,
        )

        # correct instance
        assert_equal(
            instance._id,
            2,
        )

    def test_load(self):
        instance = self.Top.load(2)

        # correct class
        assert_equal(
            instance.__class__,
            self.Bottom,
        )

        # correct instance
        assert_equal(
            instance._id,
            2
        )

    def test_gather_subclasses(self):
        assert_equal(
            set(self.Top.gather_subclasses()),
            {self.Top, self.Middle, self.Bottom}
        )
        assert_equal(
            set(self.Middle.gather_subclasses()),
            {self.Middle, self.Bottom}
        )
        assert_equal(
            set(self.Bottom.gather_subclasses()),
            {self.Bottom}
        )
        with assert_raises(RuntimeError):
            InheritableStoredObject.gather_subclasses()

    def test_gather_polymorphic_types(self):
        assert_equal(
            self.Top.gather_polymorphic_types(),
            {
                'Top': self.Top,
                'Middle': self.Middle,
                'Bottom': self.Bottom,
            }
        )
        assert_equal(
            self.Middle.gather_polymorphic_types(),
            {
                'Middle': self.Middle,
                'Bottom': self.Bottom,
            }
        )
        assert_equal(
            self.Bottom.gather_polymorphic_types(),
            {
                'Bottom': self.Bottom,
            }
        )

    def test_to_storage(self):
        assert_equal(
            self.top.to_storage()['__polymorphic_type'],
            'Top',
        )
        assert_equal(
            self.middle.to_storage()['__polymorphic_type'],
            'Middle',
        )
        assert_equal(
            self.bottom.to_storage()['__polymorphic_type'],
            'Bottom',
        )