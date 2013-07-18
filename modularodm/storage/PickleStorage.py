from ..storage import Storage
from ..storage import KeyExistsException

import copy
import os
try:
    import cpickle as pickle
except ImportError:
    import pickle

class PickleStorage(Storage):
    """ Storage backend using pickle. """

    def __init__(self, collection_name,  prefix='db_', ext='pkl'):
        """Build pickle file name and load data if exists.

        :param collection_name: Collection name
        :param prefix: File prefix; defaults to 'db_'
        :param ext: File extension; defaults to 'pkl'

        """
        # Build filename
        self.filename = prefix + collection_name + '.' + ext

        # Initialize empty store
        self.store = {}

        # Load file if exists
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as fp:
                data = fp.read()
                self.store = pickle.loads(data)

    def insert(self, key, value):
        """Add key-value pair to storage. Key must not exist.

        :param key: Key
        :param value: Value

        """
        if key not in self.store:
            self.store[key] = value
            self.flush()
        else:
            msg = 'Key ({key}) already exists'.format(key=key)
            raise KeyExistsException(msg)

    def update(self, key, value):
        """Update value of key. Key need not exist.

        :param key: Key
        :param value: Value

        """
        self.store[key] = value
        self.flush()

    def get(self, key):
        return self.store[key]

    def remove(self, key):
        """Retrieve value from store.

        :param key: Key

        """
        del self.store[key]
        self.flush()

    def flush(self):
        """ Save store to file. """
        with open(self.filename, 'wb') as fp:
            pickle.dump(self.store, fp, -1)

    def find_all(self):
        return self.store.values()
    
    def __repr__(self):
        return str(self.store)