import unittest
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields, exceptions
from tests.base import ModularOdmTestCase

class TestMigration(ModularOdmTestCase):

    def define_objects(self):

        # Use a single storage object for both schema versions
        _storage = self.make_storage()

        class V1(StoredObject):
            _id = fields.StringField(primary=True, index=True)
            my_string = fields.StringField()
            my_float = fields.FloatField()
            my_number = fields.FloatField()
            my_null = fields.StringField(required=False)
            _meta = {
                'version': 1,
                'optimistic': True
            }
        V1.set_storage(_storage)

        class V2(StoredObject):
            _id = fields.StringField(primary=True, index=True)
            my_string = fields.StringField()
            my_int = fields.IntegerField(default=5)
            my_number = fields.IntegerField()

            @classmethod
            def _migrate(cls, old, new):
                new.my_string = old.my_string + 'yo'
                if old.my_number:
                    new.my_number = int(old.my_number)

            _meta = {
                'version_of': V1,
                'version': 2,
                'optimistic': True
            }
        V2.set_storage(_storage)

        return V1, V2

    def set_up_objects(self):
        self.record = self.V1(my_string='hi', my_float=1.2, my_number=3.4)
        self.record.save()
        self.migrated_record = self.V2.load(self.record._primary_key)

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

    def test_making_field_required(self):
        self.V2.migrate_all()
        # Need default value
        assert_raises(exceptions.ValidationError,
                        lambda: self.V2.migrate_all())


if __name__ == '__main__':
    unittest.main()
