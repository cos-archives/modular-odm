"""

"""

import time
import random
import string
import logging
from functools import wraps
import itertools
import operator

from ..translators import DefaultTranslator
from ..translators import JSONTranslator
from ..translators import StringTranslator

class KeyExistsException(Exception): pass

class Logger(object):

    def __init__(self):

        self.listening = False
        self.events = []

    def listen(self):

        if self.listening:
            return False

        self.listening = True
        self.events = []
        return True

    def record_event(self, event):

        if self.listening:
            self.events.append(event)

    def report(self):

        out = {}

        comparator = operator.attrgetter('func_name')
        heard = sorted(self.events, key=comparator)
        for key, group in itertools.groupby(heard, comparator):
            group = list(group)
            num_events = len(group)
            total_time = sum([event.elapsed_time for event in group])
            out[key] = (num_events, total_time)

        return out

    def clear(self):

        self.listening = False
        self.events = []

class LogEvent(object):

    def __init__(self, func_name, start_time, stop_time):

        self.func_name = func_name
        self.start_time = start_time
        self.stop_time = stop_time
        self.elapsed_time = stop_time - start_time

    def __repr__(self):

        return 'LogEvent("{func_name}", {start_time}, {stop_time})'.format(
            **self.__dict__
        )

def logify(func):

    @wraps(func)
    def wrapped(this, *args, **kwargs):

        if this.logger.listening:
            start_time = time.time()

        out = func(this, *args, **kwargs)

        if this.logger.listening:
            stop_time = time.time()
            this.logger.record_event(LogEvent(func.__name__, start_time, stop_time))

        return out

    return wrapped

class StorageMeta(type):

    def __new__(mcs, name, bases, dct):

        for key, value in dct.items():

            if not hasattr(value, '__call__'):
                continue
            if isinstance(value, type):
                continue
            if key.startswith('_') or key.endswith('_'):
                continue

            dct[key] = logify(value)

        # if not issubclass(mcs, Storage):
        dct['logger'] = Logger()

        # Run super-metaclass __new__
        return super(StorageMeta, mcs).__new__(mcs, name, bases, dct)

class Storage(object):
    """Abstract base class for storage objects. Subclasses (e.g. PickleStorage,
    MongoStorage, etc.) must define insert, update, get, remove, flush, and
    find_all methods.

    """

    __metaclass__ = StorageMeta
    Translator = DefaultTranslator

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