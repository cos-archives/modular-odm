import abc
import six
import weakref


@six.add_metaclass(abc.ABCMeta)
class BaseKeyedObject(object):
    """Abstract mixin exposing a `key` property.

    """
    @abc.abstractproperty
    def key(self):
        pass


class KeyedProperty(object):
    """Descriptor keyed on the `key` property of its parent class. Intended
    for use in subclasses of `BaseKeyedObject`.

    :param default: Default property value; will be called on assignment if
        callable

    """
    def __init__(self, default=None):
        self.data = weakref.WeakKeyDictionary()
        self.default = default

    def ensure_instance_key(self, instance):
        try:
            self.data[instance]
        except KeyError:
            self.data[instance] = {}

    def __get__(self, instance, owner):
        self.ensure_instance_key(instance)
        try:
            return self.data[instance][instance.key]
        except KeyError:
            value = self.default() if callable(self.default) else self.default
            self.data[instance][instance.key] = value
            return value

    def __set__(self, instance, value):
        self.ensure_instance_key(instance)
        self.data[instance][instance.key] = value
