from dateutil import parser as dateparser
from bson import ObjectId

class DefaultTranslator(object):

    null_value = None

    def to_default(self, value):
        return value

    def from_default(self, value):
        return value

    def to_ObjectId(self, value):
        return str(value)

    def from_ObjectId(self, value):
        return ObjectId(value)

class JSONTranslator(DefaultTranslator):

    def to_datetime(self, value):
        return str(value)

    def from_datetime(self, value):
        return dateparser.parse(value)

class StringTranslator(JSONTranslator):

    null_value = 'none'

    def to_default(self, value):
        return str(value)

    def from_integer(self, value):
        return int(value)

    def from_float(self, value):
        return float(value)

    def from_boolean(self, value):
        return bool(value)