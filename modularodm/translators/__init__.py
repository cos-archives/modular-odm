
import dateutil

class DefaultTranslator(object):

    def to_default(self, value):
        return value

    def from_default(self, value):
        return value

class JSONTranslator(DefaultTranslator):

    def to_datetime(self, value):
        return str(value)

    def from_datetime(self, value):
        return dateutil.parser.parse(value)
