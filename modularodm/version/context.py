from modularodm import StoredObject

class VersionContext(object):

    def __init__(self, date, object_class=StoredObject):
        self.date = date
        self.object_class = object_class

    def __enter__(self):
        self.date_backup = getattr(
            self.object_class, '_version_date', None
        )
        self.object_class._version_date = self.date

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.object_class._version_data = self.date_backup
