import os
from modularodm import StoredObject, fields, storage

try:
    os.remove('db_migrate_sandbox.pkl')
except OSError:
    pass

my_storage = storage.PickleStorage('migrate_sandbox')

class Schema1(StoredObject):

    _id = fields.StringField(primary=True)
    number = fields.IntegerField()
    deleted = fields.FloatField()

    _meta = {
        'optimistic': True,
        'version': 1,
    }

Schema1.set_storage(my_storage)

class Schema2(StoredObject):

    _id = fields.StringField(primary=True)
    name = fields.StringField(default='name')
    number = fields.IntegerField()

    @classmethod
    def _migrate(self, old, new):
        new.number = old.number + 1
        return new

    @classmethod
    def _unmigrate(cls, new, old):
        old.number = new.number - 1
        return old

    _meta = {
        'optimistic': True,
        'version': 2,
        'version_of': Schema1,
    }

Schema2.set_storage(my_storage)

class Schema3(StoredObject):

    _id = fields.StringField(primary=True)
    name = fields.StringField(default='eman')
    number = fields.IntegerField()

    @classmethod
    def _migrate(self, old, new):
        new.number = old.number + 1
        return new

    @classmethod
    def _unmigrate(cls, new, old):
        old.number = new.number - 1
        return old

    _meta = {
        'optimistic': True,
        'version': 3,
        'version_of': Schema2,
    }

Schema3.set_storage(my_storage)

# Describe migration from Schema1 -> Schema2 -> Schema3
Schema3.explain_migration()

# Create a record of type Schema1, then migrate to Schema3
record = Schema1(number=1)
record.save()
migrated_record = Schema3.load(record._primary_key)
print 'name', migrated_record.name        # Should be "eman"
print 'number', migrated_record.number    # Should be 3
