# -*- coding: utf-8 -*-
from nose.tools import *  # PEP8 asserts

from modularodm import fields, StoredObject
from modularodm.query.query import RawQuery as Q

from tests.base import ModularOdmTestCase


class TestForeignQueries(ModularOdmTestCase):

    def define_objects(self):

        class Foo(StoredObject):
            _id = fields.StringField(primary=True)
            _meta = {
                'optimistic': True,
            }

        class Bar(StoredObject):
            _id = fields.StringField(primary=True)
            ref = fields.ForeignField('foo', backref='my_ref')
            abs_ref = fields.AbstractForeignField(backref='my_abs_ref')
            ref_list = fields.ForeignField('foo', backref='my_ref_list', list=True)
            abs_ref_list = fields.AbstractForeignField(backref='my_abs_ref_list', list=True)
            _meta = {
                'optimistic': True,
            }

        return Foo, Bar

    def set_up_objects(self):

        self.foos = []
        for _ in range(5):
            foo = self.Foo()
            foo.save()
            self.foos.append(foo)

    def test_eq_foreign(self):

        bar = self.Bar(ref=self.foos[0])
        bar.save()

        result = self.Bar.find(
            Q('ref', 'eq', self.foos[0])
        )
        assert_equal(len(result), 1)

        result = self.Bar.find(
            Q('ref', 'eq', self.foos[-1])
        )
        assert_equal(len(result), 0)

    def test_eq_foreign_list(self):

        bar = self.Bar(ref_list=self.foos[:3])
        bar.save()

        result = self.Bar.find(
            Q('ref_list', 'eq', self.foos[0])
        )
        assert_equal(len(result), 1)

        result = self.Bar.find(
            Q('ref_list', 'eq', self.foos[-1])
        )
        assert_equal(len(result), 0)

    def test_eq_abstract(self):

        bar = self.Bar(abs_ref=self.foos[0])
        bar.save()

        result = self.Bar.find(
            Q('abs_ref', 'eq', self.foos[0])
        )
        assert_equal(len(result), 1)

        result = self.Bar.find(
            Q('abs_ref', 'eq', self.foos[-1])
        )
        assert_equal(len(result), 0)

    def test_eq_abstract_list(self):

        bar = self.Bar(abs_ref_list=self.foos[:3])
        bar.save()

        result = self.Bar.find(
            Q('abs_ref_list', 'eq', self.foos[0])
        )
        assert_equal(len(result), 1)

        result = self.Bar.find(
            Q('abs_ref_list', 'eq', self.foos[-1])
        )
        assert_equal(len(result), 0)
