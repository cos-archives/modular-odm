# -*- coding: utf-8 -*-

from flask import request

from modularodm.cache import Cache
from modularodm.writequeue import WriteQueue
from modularodm.storedobject import StoredObject

from .concurrency import BaseKeyedObject, KeyedProperty


# `FlaskKeyedObject`s should work when outside a request context, so we use
# a dummy key in this case. Because we can't create weak references to some
# types (str, NoneType, etc.), use an object as the dummy key.
class DummyRequest(object):
    pass
dummy_request = DummyRequest()


class FlaskKeyedObject(BaseKeyedObject):
    """Mixin that provides a `key` property that resolves to the current
    Flask request, or to a dummy request object if not in a Flask request
    context.

    """
    @property
    def key(self):
        try:
            return request._get_current_object()
        except RuntimeError:
            return dummy_request


class FlaskCache(Cache, FlaskKeyedObject):
    """Subclass of `Cache` with `data` keyed on the current Flask request.

    """
    data = KeyedProperty(lambda: dict())


class FlaskWriteQueue(WriteQueue, FlaskKeyedObject):
    """Subclass of `WriteQueue` with `data` keyed on the current Flask request.

    """
    actions = KeyedProperty()
    active = KeyedProperty()


class FlaskStoredObject(StoredObject):
    """Subclass of StoredObject with cache and write queue keyed on the
    current request.

    """
    _cache = FlaskCache()
    _object_cache = FlaskCache()
    queue = FlaskWriteQueue()
