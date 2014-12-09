import six

from .. import StoredObject
from ..query.querydialect import DefaultQueryDialect as Q
from ..storedobject import ObjectMeta


class InheritableObjectMeta(ObjectMeta):
    """Metaclass for InheritableStoredObject - tightly coupled"""
    def __init__(cls, name, bases, dct):

        super(InheritableObjectMeta, cls).__init__(name, bases, dct)

        # If this is the base for inheritable objects, return
        if cls.__name__ == 'InheritableStoredObject':
            return

        # Walk up the inheritance tree until we get to the direct descendant of
        #  InheritableStoredObject (the base inheritable)
        inherited_class = cls
        inherited_bases = bases
        while 'InheritableStoredObject' != inherited_bases[0].__name__:
            inherited_class = inherited_bases[0]
            inherited_bases = inherited_bases[0].__bases__

        # Set the collection for this class to that of the base inheritable
        cls._name = inherited_class._name

        # Set default value for __polymorphic_type
        if not hasattr(cls, '__polymorphic_type'):
            cls.__polymorphic_type = cls.__name__


@six.add_metaclass(InheritableObjectMeta)
class InheritableStoredObject(StoredObject):
    """StoredObject subclass for models which will share a single collection.

    Modeled after SQLAlchemy's "Joined Table Inheritance":
        http://docs.sqlalchemy.org/en/rel_0_9/orm/inheritance.html
    """

    def __init__(self, *args, **kwargs):
        # Polymorphic type
        pt = kwargs.get('__polymorphic_type',
                        self._InheritableObjectMeta__polymorphic_type)
        # Dynamically reclass the object being constructed to the correct class
        self.__class__ = self.gather_polymorphic_types().get(pt, self)

        super(InheritableStoredObject, self).__init__(*args, **kwargs)

    @classmethod
    def find(cls, query=None, **kwargs):
        # apply restrictions
        query = cls._build_query_filter(query)
        return super(InheritableStoredObject, cls).find(query, **kwargs)

    @classmethod
    def find_one(cls, query=None, **kwargs):
        # apply restrictions
        query = cls._build_query_filter(query)
        return super(InheritableStoredObject, cls).find_one(query, **kwargs)

    @classmethod
    def _build_query_filter(cls, query):
        """Restrict query to include only the appropriate polymorphic IDs"""
        # build a list of Query objects, one for each subclass
        query_parts = [
            Q('__polymorphic_type', 'eq', sub._InheritableObjectMeta__polymorphic_type)
            for sub in cls.gather_subclasses()
        ]

        # assemble a filter queryset
        filter = query_parts.pop()
        for part in query_parts:
            filter |= part

        # require that the filter be met in addition to the provided query
        if query is not None:
            query &= filter
        else:
            query = filter

        return query

    @classmethod
    def gather_subclasses(cls):
        """Return a set of classes which inherent from this one"""
        if cls is InheritableStoredObject:
            raise RuntimeError("Cannot gather subclasses for inheritable base")
        subclasses = set()
        for sub in cls.__subclasses__():
            subclasses = subclasses | sub.gather_subclasses()
        subclasses.add(cls)
        return subclasses

    @classmethod
    def gather_polymorphic_types(cls):
        """Return a dict mapping polymorphic types to classes"""
        return {
            sub._InheritableObjectMeta__polymorphic_type: sub
            for sub in cls.gather_subclasses()
        }

    @classmethod
    def register_collection(cls):
        # Prevent registration unless this is the base inheritable class
        if InheritableStoredObject in cls.__bases__:
            super(InheritableStoredObject, cls).register_collection()

    def to_storage(self, *args, **kwargs):
        data = super(InheritableStoredObject, self).to_storage(*args, **kwargs)
        # Add polymorhic type to the serialized object
        data['__polymorphic_type'] = self._InheritableObjectMeta__polymorphic_type
        return data