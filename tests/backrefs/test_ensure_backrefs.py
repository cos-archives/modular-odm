# -*- coding: utf-8 -*-
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields
from modularodm.storedobject import ensure_backrefs
from tests.base import ModularOdmTestCase

class TestEnsureBackrefs(ModularOdmTestCase):

    def define_objects(self):

        class Foo(StoredObject):
            _id = fields.StringField()
            _meta = {
                'optimistic': True,
            }

        class Bar(StoredObject):
            _id = fields.StringField()
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

    def test_ensure_foreign(self):

        bar = self.Bar(ref=self.foos[0])
        bar.save()

        # Delete backrefs for some reason
        self.foos[0]._StoredObject__backrefs = {}
        self.foos[0].save()

        # Assert that backrefs are gone
        assert_equal(
            len(self.foos[0].bar__my_ref),
            0
        )

        # Restore backrefs
        ensure_backrefs(bar)

        # Assert that backrefs are correct
        assert_equal(
            len(self.foos[0].bar__my_ref),
            1
        )
        assert_equal(
            self.foos[0].bar__my_ref[0],
            bar
        )

    def test_ensure_foreign_list(self):

        bar = self.Bar(ref_list=self.foos)
        bar.save()

        for foo in self.foos:

            # Delete backrefs for some reason
            foo._StoredObject__backrefs = {}
            foo.save()

            # Assert that backrefs are gone
            assert_equal(
                len(foo.bar__my_ref_list),
                0
            )

        # Restore backrefs
        ensure_backrefs(bar)

        for foo in self.foos:

            # Assert that backrefs are correct
            assert_equal(
                len(foo.bar__my_ref_list),
                1
            )
            assert_equal(
                foo.bar__my_ref_list[0],
                bar
            )
