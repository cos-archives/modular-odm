from ..storage import Storage
import os
try:
    import cpickle as pickle
except:
    import pickle

class PickleStorage(Storage):
    def __init__(self, collection_name,  prefix='db_', ext='pkl'):
        self.filename = prefix + collection_name + '.' + ext

        self.store = {}

        if os.path.exists(self.filename):
            fi = open(self.filename, 'rb')
            data = fi.read()
            self.store = pickle.loads(data)
            fi.close()

    def insert(self, key, value):
        if not key in self.store:
            self.store[key] = value
            self.flush()
        else:
            msg = 'Key ({key}) already exists'.format(key=key)
            raise Exception(msg)

    def update(self, key, value):
        self.store[key] = value
        self.flush()

    def get(self, key):
        return self.store[key]

    def remove(self, key):
        del self.store[key]
        self.flush()

    def flush(self):
        fi = open(self.filename, 'wb')
        pickle.dump(self.store, fi, -1)
        fi.close()

    def find_all(self):
        return self.store.values()
    
    def __repr__(self):
        return str(self.store)