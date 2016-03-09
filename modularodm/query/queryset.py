# -*- coding: utf-8 -*-

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseQuerySet(object):

    _NEGATIVE_INDEXING = False

    def __init__(self, schema, data=None):

        self.schema = schema
        self.primary = schema._primary_name
        self.data = data

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step:
                raise IndexError('Slice steps not supported')
            if (index.start is not None and index.start < 0) or (index.stop is not None and index.stop < 0):
                raise IndexError('Negative indexing not supported')
            if index.stop is not None and index.stop < index.start:
                raise IndexError('Stop index must be greater than start index')
        elif not self.__class__._NEGATIVE_INDEXING and index < 0:
            raise IndexError('Negative indexing not supported')
        return self._do_getitem(index)

    @abc.abstractmethod
    def _do_getitem(self, index):
        pass

    @abc.abstractmethod
    def __iter__(self):
        pass

    @abc.abstractmethod
    def __len__(self):
        pass

    @abc.abstractmethod
    def count(self):
        pass

    @abc.abstractmethod
    def sort(self, *keys):
        pass

    @abc.abstractmethod
    def offset(self, n):
        pass

    @abc.abstractmethod
    def limit(self, n):
        pass
