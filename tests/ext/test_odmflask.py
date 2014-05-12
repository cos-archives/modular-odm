# -*- coding: utf-8 -*-

import unittest
from nose.tools import *

from flask import Flask

from modularodm.writequeue import WriteAction
from modularodm.ext import odmflask


class TestConcurrency(unittest.TestCase):

    def setUp(self):
        self.app = Flask('test')
        self.context = self.app.test_request_context()

    def test_get_key_default(self):
        assert_equal(
            odmflask.get_flask_key(),
            odmflask.dummy_request
        )

    def test_get_key_request(self):
        self.context.push()
        assert_equal(
            odmflask.get_flask_key(),
            self.context.request
        )

    def test_cache(self):

        action1 = WriteAction(max, 1, 2, 3)
        odmflask.FlaskStoredObject.queue.start()
        odmflask.FlaskStoredObject.queue.push(action1)
        assert_equal(
            odmflask.FlaskStoredObject.queue.actions[0],
            action1
        )

        self.context.push()
        assert_false(odmflask.FlaskStoredObject.queue.active)
        assert_false(odmflask.FlaskStoredObject.queue.actions)
        action2 = WriteAction(min, 1, 2, 3)
        odmflask.FlaskStoredObject.queue.start()
        odmflask.FlaskStoredObject.queue.push(action2)
        assert_equal(
            odmflask.FlaskStoredObject.queue.actions[0],
            action2
        )

        self.context.pop()
        assert_equal(
            odmflask.FlaskStoredObject.queue.actions[0],
            action1
        )


if __name__ == '__main__':
    unittest.main()
