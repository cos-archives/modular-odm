
from modularodm import StoredObject

class Query(object):

    def __init__(self, attr=None, oper='eq', valu=None):

        if isinstance(valu, StoredObject):
            valu = valu._primary_key

        self.attr = attr
        self.oper = oper
        self.valu = valu