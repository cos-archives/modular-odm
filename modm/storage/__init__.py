import random

class Storage:
    def _generate_random_id(self, n=5):
        NUMBERS = '23456789'
        LOWERS = 'abcdefghijkmnpqrstuvwxyz'
        UPPERS = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        return ''.join(random.sample(NUMBERS+LOWERS+UPPERS, n))

    def optimistic_insert(self, value, label, n=5):
        while True:
            try:
                key = self._generate_random_id(n)
                value[label] = key
                self.insert(key, value)
            except:
                continue
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