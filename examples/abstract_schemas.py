"""Example of using abstract schemas as superclasses of concrete schemas. The
abstract BaseSchema class cannot be instantiated, but the Schema class can be.
"""

from modularodm import StoredObject, fields
from bson import ObjectId

class BaseSchema(StoredObject):

    _id = fields.StringField(default=lambda: str(ObjectId()))

    _meta = {
        'abstract': True,
    }

class Schema(BaseSchema):

    data = fields.StringField()

# Instantiate Schema
record = Schema(data='test')
print record._id  # Yields an ObjectId-like primary key

# Can't instantiate abstract schema
try:
    bad_record = BaseSchema()
except TypeError as error:
    print error
