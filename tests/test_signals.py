# -*- coding: utf-8 -*-

import mock
import unittest
from nose.tools import *

from tests.utils import make_model

from modularodm import StoredObject


class TestSignals(unittest.TestCase):

    def setUp(self):
        self.model = make_model()

    @mock.patch('modularodm.storedobject.signals.save.connect_via')
    def test_subscribe_weak(self, mock_connect_via):
        self.model.subscribe('save', weak=True)
        mock_connect_via.assert_called_once_with(
            self.model,
            True,
        )

    @mock.patch('modularodm.storedobject.signals.save.connect_via')
    def test_subscribe_strong(self, mock_connect_via):
        self.model.subscribe('save', weak=False)
        mock_connect_via.assert_called_once_with(
            self.model,
            False,
        )

    @mock.patch('modularodm.storedobject.signals.save.connect_via')
    def test_subscribe_from_base_schema(self, mock_connect_via):
        StoredObject.subscribe('save', weak=False)
        mock_connect_via.assert_called_once_with(
            None,
            False
        )

    def _subscribe_mock(self, signal_name, weak):
        """Create a mock callback function and subscribe it to the specific
        signal on ``self.model``.

        """
        callback = mock.Mock()
        decorator = self.model.subscribe(signal_name, weak)
        return decorator(callback)

    def test_before_save(self):

        connected_callback = self._subscribe_mock('before_save', weak=False)

        record = self.model(_id=1)
        record.save()

        connected_callback.assert_called_once_with(
            record.__class__, instance=record,
        )

    def test_save(self):

        connected_callback = self._subscribe_mock('save', weak=False)

        record = self.model(_id=1)
        record.save()

        connected_callback.assert_called_once_with(
            record.__class__,
            instance=record,
            fields_changed={'_id', 'value'},
            cached_data={},
        )

    def test_load(self):

        connected_callback = self._subscribe_mock('load', weak=False)

        record = self.model(_id=1)
        record.save()
        self.model.load(1)

        connected_callback.assert_called_once_with(
            record.__class__,
            key=1,
            data=None,
        )
