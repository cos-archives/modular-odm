import unittest
from nose.tools import *  # PEP8 asserts

from modularodm import StoredObject, fields
from tests.base import ModularOdmTestCase

class TestMigration(ModularOdmTestCase):

    def define_objects(self):

        # Use a single storage object for both schema versions
        _storage = self.make_storage()

        class V1(StoredObject):
            _id = fields.StringField()
            my_string = fields.StringField()
            my_float = fields.FloatField()
            _meta = {
                'optimistic': True,
                'version': 1,
            }
        V1.set_storage(_storage)

        class V2(StoredObject):
            _id = fields.StringField()
            my_string = fields.StringField()
            my_int = fields.IntegerField(default=5)
            @classmethod
            def _migrate(cls, old, new):
                new.my_string = old.my_string + 'yo'
            _meta = {
                'optimistic': True,
                'version_of': V1,
                'version': 2,
            }
        V2.set_storage(_storage)

        return V1, V2

    def set_up_objects(self):

        self.record = self.V1(my_string='hi')
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

    def test_save_migrated(self):

        try:
            self.migrated_record.save()
        except:
            assert False

if __name__ == '__main__':
    unittest.main()
