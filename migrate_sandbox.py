
# todo add hooks for on_before_migrate, on_after_migrate
# todo dry run

from modularodm import StoredObject, fields, storage
from modularodm.validators import MinLengthValidator

class Foo(StoredObject):

    _id = fields.StringField(primary=True)
    name = fields.StringField()
    number = fields.IntegerField()
    bar = fields.ForeignField('bar')

    _meta = {
        'optimistic' : True,
        'version' : 1,
    }

Foo.set_storage(storage.PickleStorage('migrate_foo'))

class OldOldBar(StoredObject):

    _id = fields.StringField(primary=True)
    number = fields.IntegerField()

    _meta = {
        'optimistic' : True,
        'version' : 1,
    }

OldOldBar.set_storage(storage.PickleStorage('migrate_bar'))

class OldBar(StoredObject):

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
        'optimistic' : True,
        'version' : 2,
        'version_of' : OldOldBar,
    }

OldBar.set_storage(storage.PickleStorage('migrate_bar'))

class Bar(StoredObject):

    _id = fields.StringField(primary=True)
    name = fields.StringField(default='eman')#, validate=MinLengthValidator(2))
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
        'optimistic' : True,
        'version' : 3,
        'version_of' : OldBar,
    }

Bar.set_storage(storage.PickleStorage('migrate_bar'))

def setup():

    bars = []
    for idx in range(5):
        bar = Bar(number=idx)
        bar.save()
        bars.append(bar)

    foo1 = Foo(name='foo1', number=0, bar=bars[0])
    foo1.save()

    foo2 = Foo(name='foo2', number=1, bar=bars[1])
    foo2.save()

# setup()

test = Bar.load('4iAxL')
print 'test.name', test.name
print 'test.number', test.number

Bar.explain_migration()

print 'debug'