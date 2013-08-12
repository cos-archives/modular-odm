"""

"""

import random
import string

from ..translators import DefaultTranslator
from ..translators import JSONTranslator

class KeyExistsException(Exception): pass

class Storage(object):
    """Abstract base class for storage objects. Subclasses (e.g. PickleStorage,
    MongoStorage, etc.) must define insert, update, get, remove, flush, and
    find_all methods.

    """

    Translator = DefaultTranslator
    Translator = JSONTranslator

    def _ensure_index(self, key):
        pass

    def _generate_random_id(self, n=5):
        """Generated random alphanumeric key.

        :param n: Number of characters in random key

        """
        # Build character set
        charset = string.lowercase + \
            string.uppercase + \
            string.digits

        return ''.join(random.sample(charset, n))

    def optimistic_insert(self, schema, value, n=5):
        """Attempt to insert with randomly generated key until insert
        is successful.

        :param value:
        :param label:
        :param n: Number of characters in random key

        """
        while True:
            try:
                key = self._generate_random_id(n)
                value[schema._primary_name] = key
                self.insert(schema, key, value)
            except KeyExistsException:
                pass
            break
        return key

    def insert(self, key, value):
        raise NotImplementedError

    def update(self, key, value):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def remove(self, key):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def find_all(self):
        raise NotImplementedError

    def __repr__(self):
        return str(self.store)