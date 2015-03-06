# -*- coding: utf-8 -*-

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseQuerySet(object):

    def __init__(self, schema, data=None):

        self.schema = schema
        self.primary = schema._primary_name
        self.data = data

    @abc.abstractmethod
    def __getitem__(self, index):
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
