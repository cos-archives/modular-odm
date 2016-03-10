#!/usr/bin/env python
# encoding: utf-8


from nose.tools import *

from tests.base import ModularOdmTestCase, TestObject

from modularodm import fields


class TestForeignList(ModularOdmTestCase):

    def define_objects(self):

        class Foo(TestObject):
            _id = fields.IntegerField()
            bars = fields.ForeignField('bar', list=True)

        class Bar(TestObject):
            _id = fields.IntegerField()

        return Foo, Bar

    def set_up_objects(self):

        self.foo = self.Foo(_id=1)

        self.bars = []
        for idx in range(5):
            self.bars.append(self.Bar(_id=idx))
            self.bars[idx].save()

        self.foo.bars = self.bars
        self.foo.save()

    def test_get_item(self):
        assert_equal(self.bars[2], self.foo.bars[2])

    def test_get_slice(self):
        assert_equal(self.bars[:3], list(self.foo.bars[:3]))

    def test_get_slice_extended(self):
        assert_equal(self.bars[::-1], list(self.foo.bars[::-1]))


class TestAbstractForeignList(ModularOdmTestCase):

    def define_objects(self):

        class Foo(TestObject):
            _id = fields.IntegerField()
            bars = fields.AbstractForeignField(list=True)

        class Bar(TestObject):
            _id = fields.IntegerField()

        return Foo, Bar

    def set_up_objects(self):

        self.foo = self.Foo(_id=1)

        self.bars = []
        for idx in range(5):
            self.bars.append(self.Bar(_id=idx))
            self.bars[idx].save()

        self.foo.bars = self.bars
        self.foo.save()

    def test_get_item(self):
        assert_equal(self.bars[2], self.foo.bars[2])

    def test_get_slice(self):
        assert_equal(self.bars[:3], list(self.foo.bars[:3]))

    def test_get_slice_extended(self):
        assert_equal(self.bars[::-1], list(self.foo.bars[::-1]))

