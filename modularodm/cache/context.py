from modularodm import StoredObject

class CacheContext(object):

    def __init__(self, cache_label, klass=StoredObject):
        self.cache_label = cache_label
        self.klass = klass

    def __enter__(self):
        self.cached = self.klass._deep_cache.find_one(
            {'_id' : self.cache_label}
        )
        if self.cached is None:
            return

        self.klass._clear_caches()
        for schema, records in self.cached['cache'].items():
            schema_class = self.klass.get_collection(schema)
            for key, record in records.items():
                schema_class(_is_loaded=True, **schema_class.from_storage(record))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cached is None:
            for schema, records in self.klass._object_cache.raw.items():
                for key, record in records.items():
                    if self.cache_label not in record._caches:
                        record._caches.append(self.cache_label)
                        record.save(_pop_deep_cache=False)
            self.klass._deep_cache.insert({
                '_id' : self.cache_label,
                'cache' : self.klass._cache.raw
            })