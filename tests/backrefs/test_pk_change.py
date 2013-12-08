# -*- coding: utf-8 -*-
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields
from tests.base import ModularOdmTestCase

class TestPKChange(ModularOdmTestCase):

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

        class Baz(StoredObject):
            _id = fields.StringField()
            ref = fields.ForeignField('bar', backref='my_ref')
            abs_ref = fields.AbstractForeignField(backref='my_abs_ref')
            ref_list = fields.ForeignField('bar', backref='my_ref_list', list=True)
            abs_ref_list = fields.AbstractForeignField(backref='my_abs_ref_list', list=True)
            _meta = {
                'optimistic': True,
            }

        return Foo, Bar, Baz

    def set_up_objects(self):

        self.foos = []
        self.bars = []
        for _ in range(5):
            foo = self.Foo()
            foo.save()
            self.foos.append(foo)
            bar = self.Bar()
            bar.save()
            self.bars.append(bar)

    def test_pk_changed(self):

        bar = self.Bar()
        bar.save()

        prev_key = bar._primary_key

        bar._id = 'changed'
        bar.save()

        StoredObject._clear_caches()

        assert_true(self.Bar.load(prev_key) is None)
        assert_true(self.Bar.load('changed') is not None)

    def test_backrefs_same(self):
        """Regression test: Ensure that backrefs to record are unchanged after
        changing PK.

        """
        baz = self.Baz(ref=self.bars[0])
        baz.save()

        bar = self.bars[0]

        assert_in(
            baz._primary_key,
            bar._backrefs['my_ref']['baz']['ref']
        )

        bar._id = 'changed'
        bar.save()

        assert_in(
            baz._primary_key,
            bar._backrefs['my_ref']['baz']['ref']
        )


    def test_update_foreign_referee(self):
        """Update the PK of a record with a saved foreign field; assert that
        the backrefs of the foreign object includes the new PK but not the old
        PK.

        """
        bar = self.Bar(ref=self.foos[0])
        bar.save()
        prev_key = bar._primary_key

        bar._id = 'changed'
        bar.save()

        assert_in(
            'changed',
            self.foos[0]._backrefs['my_ref']['bar']['ref']
        )
        assert_not_in(
            prev_key,
            self.foos[0]._backrefs['my_ref']['bar']['ref']
        )

    def test_update_foreign_referent(self):
        """Update the PK of a record (bar) referred to by another record (baz);
        assert that second record (baz) points to changed record (bar).

        """
        baz = self.Baz(ref=self.bars[0])
        baz.save()

        self.bars[0]._id = 'changed'
        self.bars[0].save()

        StoredObject._clear_caches()
        baz = self.Baz.load(baz._primary_key)

        assert_equal(
            baz.ref, self.bars[0]
        )

    def test_update_foreign_list_referee(self):
        """Update the PK of a record with a saved foreign list field; assert
        that the foreign objects include the new PK but not the old PK.

        """
        bar = self.Bar(ref_list=self.foos)
        bar.save()
        prev_key = bar._primary_key

        bar._id = 'changed'
        bar.save()

        for foo in self.foos:
            assert_in(
                'changed',
                foo._backrefs['my_ref_list']['bar']['ref_list']
            )
            assert_not_in(
                prev_key,
                foo._backrefs['my_ref_list']['bar']['ref_list']
            )

    def test_update_foreign_list_referent(self):
        """

        """
        baz = self.Baz(ref_list=self.bars)
        baz.save()

        self.bars[0]._id = 'changed'
        self.bars[0].save()

        StoredObject._clear_caches()
        baz = self.Baz.load(baz._primary_key)

        assert_equal(
            list(baz.ref_list),
            list(self.bars)
        )

    def test_update_abstract_referee(self):
        """Update the PK of a record with a saved abstract foreign field;
        assert that the foreign object includes the new PK but not the old PK.

        """
        bar = self.Bar(abs_ref=self.foos[0])
        bar.save()
        prev_key = bar._primary_key

        bar._id = 'changed'
        bar.save()

        assert_in(
            'changed',
            self.foos[0]._backrefs['my_abs_ref']['bar']['abs_ref']
        )
        assert_not_in(
            prev_key,
            self.foos[0]._backrefs['my_abs_ref']['bar']['abs_ref']
        )

    def test_update_abstract_referent(self):
        """

        """
        baz = self.Baz(abs_ref=self.bars[0])
        baz.save()

        self.bars[0]._id = 'changed'
        self.bars[0].save()

        StoredObject._clear_caches()
        baz = self.Baz.load(baz._primary_key)

        assert_equal(
            baz.abs_ref, self.bars[0]
        )

    def test_update_abstract_list_referee(self):
        """Update the PK of a record with a saved abstract foreign list field;
        assert that the foreign objects include the new PK but not the old PK.

        """
        bar = self.Bar(abs_ref_list=self.foos)
        bar.save()
        prev_key = bar._primary_key

        bar._id = 'changed'
        bar.save()

        for foo in self.foos:
            assert_in(
                'changed',
                foo._backrefs['my_abs_ref_list']['bar']['abs_ref_list']
            )
            assert_not_in(
                prev_key,
                foo._backrefs['my_abs_ref_list']['bar']['abs_ref_list']
            )

    def test_update_abstract_list_referent(self):
        """

        """
        baz = self.Baz(abs_ref_list=self.bars)
        baz.save()

        self.bars[0]._id = 'changed'
        self.bars[0].save()

        StoredObject._clear_caches()
        baz = self.Baz.load(baz._primary_key)

        assert_equal(
            list(baz.abs_ref_list),
            list(self.bars)
        )

    def test_update_foreign_referee_and_add(self):
        """Update the PK of a record with a saved foreign field, and add a
        new reference in the save same; assert that the foreign object includes
        the new PK but not the old PK. This test ensures that the
        _update_backref method works correctly when there is no reference
        to be updated.

        """
        bar = self.Bar(ref=self.foos[0])
        bar.save()
        prev_key = bar._primary_key

        bar._id = 'changed'
        bar.abs_ref = self.foos[1]
        bar.save()

        assert_in(
            'changed',
            self.foos[0]._backrefs['my_ref']['bar']['ref']
        )
        assert_not_in(
            prev_key,
            self.foos[0]._backrefs['my_ref']['bar']['ref']
        )

    def test_update_foreign_referee_loaded(self):
        """Update the PK of a record with a saved foreign field; assert that
        the foreign object includes the new PK but not the old PK.

        """
        bar = self.Bar(ref=self.foos[0])
        bar.save()
        prev_key = bar._primary_key

        StoredObject._clear_caches()

        bar_loaded = self.Bar.load(bar._primary_key)

        bar_loaded._id = 'changed'
        bar_loaded.save()

        self.foos[0].reload()

        assert_in(
            'changed',
            self.foos[0]._backrefs['my_ref']['bar']['ref']
        )
        assert_not_in(
            prev_key,
            self.foos[0]._backrefs['my_ref']['bar']['ref']
        )
