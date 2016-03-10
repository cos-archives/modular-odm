import unittest
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields, exceptions
from tests.base import ModularOdmTestCase

class TestMigration(ModularOdmTestCase):

    def define_objects(self):

        # Use a single storage object for both schema versions
        self._storage = self.make_storage()

        class V1(StoredObject):
            _id = fields.StringField(_primary_key=True, index=True)
            my_string = fields.StringField()
            my_float = fields.FloatField()
            my_number = fields.FloatField()
            my_null = fields.StringField(required=False)
            _meta = {
                'optimistic': True,
                'version': 1,
                'optimistic': True
            }
        V1.set_storage(self._storage)

        class V2(StoredObject):
            _id = fields.StringField(_primary_key=True, index=True)
            my_string = fields.StringField()
            my_int = fields.IntegerField(default=5)
            my_number = fields.IntegerField()
            my_null = fields.StringField(required=False)

            @classmethod
            def _migrate(cls, old, new):
                if old.my_string:
                    new.my_string = old.my_string + 'yo'
                if old.my_number:
                    new.my_number = int(old.my_number)

            _meta = {
                'optimistic': True,
                'version_of': V1,
                'version': 2,
                'optimistic': True
            }
        V2.set_storage(self._storage)

        return V1, V2

    def set_up_objects(self):
        self.record = self.V1(my_string='hi', my_float=1.2, my_number=3.4)
        self.record.save()
        self.migrated_record = self.V2.load(self.record._primary_key)
        self.migrated_record.save()

    def test_version_number(self):
        assert_equal(self.migrated_record._version, 2)

    def test_new_field(self):
        assert_in('my_int', self.migrated_record._fields)
        assert_equal(self.migrated_record.my_int, 5)

    def test_deleted_field(self):
        assert_in('my_float', self.record._fields)
        assert_not_in('my_float', self.migrated_record._fields)

    def test_migrated_field(self):
        assert_equal(self.migrated_record.my_string, 'hiyo')

    def test_versions_contain_same_records(self):
        for i in range(5):
            record = self.V1(my_string="foo")
            record.save()
        assert_equal(len(self.V1.find()), len(self.V2.find()))
        # Primary keys are the same
        for old_rec, new_rec in zip(self.V1.find(), self.V2.find()):
            assert_equal(old_rec._primary_key, new_rec._primary_key)

    def test_changed_number_type_field(self):
        assert_true(isinstance(self.migrated_record._fields['my_number'],
                    fields.IntegerField))
        assert_true(isinstance(self.migrated_record.my_number, int))
        assert_equal(self.migrated_record.my_number, int(self.record.my_number))

    def test_making_field_required_without_default_raises_error(self):
        # TODO: This test raises a warning for setting a non-field value
        class V3(StoredObject):
            _id = fields.StringField(_primary_key=True, index=True)
            my_string = fields.StringField()
            my_int = fields.IntegerField(default=5)
            my_number = fields.IntegerField()
            my_null = fields.StringField(required=True)

            _meta = {
                'optimistic': True,
                'version_of': self.V2,
                'version': 3,
                'optimistic': True
            }
        V3.set_storage(self._storage)
        migrated = V3.load(self.migrated_record._primary_key)
        assert_raises(exceptions.ValidationError, lambda: migrated.save())

    def test_making_field_required_with_default(self):
        class V3(StoredObject):
            _id = fields.StringField(_primary_key=True, index=True)
            my_string = fields.StringField()
            my_int = fields.IntegerField(default=5)
            my_number = fields.IntegerField()
            my_null = fields.StringField(required=True)
            @classmethod
            def _migrate(cls, old, new):
                if not old.my_null:
                    new.my_null = 'default'
            _meta = {
                'optimistic': True,
                'version_of': self.V2,
                'version': 3,
                'optimistic': True
            }
        V3.set_storage(self._storage)
        old = self.V1()
        old.save()
        migrated = V3.load(old._primary_key)
        migrated.save()
        assert_equal(migrated.my_null, "default")

    def test_migrate_all(self):
        for i in range(5):
            rec = self.V1(my_string="foo{0}".format(i))
            rec.save()
        self.V2.migrate_all()
        # TODO: This used to be self.V2.find() (without the "count")
        #       WHY WOULD THIS WORK?!
        assert_greater_equal(self.V2.find().count(), 5)
        for record in self.V2.find():
            assert_true(record.my_string.endswith("yo"))

    def test_save_migrated(self):
        try:
            self.migrated_record.save()
        except:
            assert False

if __name__ == '__main__':
    unittest.main()
