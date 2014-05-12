import unittest
from nose.tools import *

from modularodm import writequeue

from tests.utils import make_model


class TestWriteAction(unittest.TestCase):

    def test_init(self):
        key = lambda x: -1 * x
        action = writequeue.WriteAction(
            max,
            1, 2, 3,
            key=key
        )
        assert_equal(action.method, max)
        assert_equal(action.args, (1, 2, 3))
        assert_equal(action.kwargs, {'key': key})

    def test_init_method_not_callable(self):
        with assert_raises(TypeError):
            writequeue.WriteAction(None)

    def test_execute(self):
        action = writequeue.WriteAction(
            max,
            1, 2, 3,
            key=lambda x: -1 * x
        )
        assert_equal(action.execute(), 1)


class TestWriteQueue(unittest.TestCase):

    def setUp(self):
        self.queue = writequeue.WriteQueue()
        self.queue.start()

    def test_init(self):
        assert_equal(self.queue.actions, [])

    def test_push(self):
        action1 = writequeue.WriteAction(min)
        action2 = writequeue.WriteAction(max)
        self.queue.push(action1)
        self.queue.push(action2)
        assert_equal(self.queue.actions, [action1, action2])

    def test_push_invalid(self):
        with assert_raises(TypeError):
            self.queue.push(None)

    def test_commit(self):
        action1 = writequeue.WriteAction(min, 1, 2)
        action2 = writequeue.WriteAction(max, 1, 2)
        self.queue.push(action1)
        self.queue.push(action2)
        results = self.queue.commit()
        assert_equal(results, [1, 2])
        assert_equal(self.queue.actions, [])

    def test_clear(self):
        action1 = writequeue.WriteAction(min)
        action2 = writequeue.WriteAction(max)
        self.queue.push(action1)
        self.queue.push(action2)
        self.queue.clear()
        assert_equal(self.queue.actions, [])

    def test_bool_true(self):
        self.queue.push(writequeue.WriteAction(zip))
        assert_true(self.queue)

    def test_bool_false(self):
        queue = writequeue.WriteQueue()
        assert_false(queue)


class QueueTestCase(unittest.TestCase):

    def setUp(self):
        self.Model = make_model()
        self.Model.queue.clear()

    def enqueue_record(self, _id=1):
        record = self.Model(_id=_id)
        record.save()
        return record


class TestQueueContext(QueueTestCase):

    def test_context(self):
        with writequeue.QueueContext(self.Model):
            self.enqueue_record()
            assert_false(self.Model._storage[0].insert.called)
        assert_true(self.Model._storage[0].insert.called)


class TestModelQueue(QueueTestCase):

    def test_queue_initial(self):
        assert_false(self.Model.queue)
        assert_false(self.Model.queue.active)

    def test_start_queue(self):
        self.Model.start_queue()
        assert_true(isinstance(self.Model.queue, writequeue.WriteQueue))
        assert_equal(self.Model.queue.actions, [])

    def test_start_queue_again(self):
        self.Model.start_queue()
        self.enqueue_record()
        queue = self.Model.queue
        self.Model.start_queue()
        assert_true(self.Model.queue is queue)

    def test_save_no_queue(self):
        self.enqueue_record()
        assert_true(self.Model._storage[0].insert.called)

    def test_save_queue(self):
        self.Model.start_queue()
        self.enqueue_record()
        assert_false(self.Model._storage[0].insert.called)

    def test_clear_queue(self):
        self.Model.start_queue()
        self.Model.clear_queue()
        assert_false(self.Model.queue)
        assert_false(self.Model.queue.active)

    def test_cancel_queue(self):
        self.Model.start_queue()
        self.enqueue_record()
        self.Model.cancel_queue()
        assert_false(self.Model.queue)
        assert_false(self.Model.queue.active)
        assert_false(self.Model._cache)

    def test_cancel_queue_empty(self):
        self.enqueue_record()
        self.Model.start_queue()
        self.Model.cancel_queue()
        assert_false(self.Model.queue)
        assert_false(self.Model.queue.active)
        assert_true(self.Model._cache)

    def test_commit_queue(self):
        self.Model.start_queue()
        self.enqueue_record()
        assert_false(self.Model._storage[0].insert.called)
        self.Model.commit_queue()
        assert_true(self.Model._storage[0].insert.called)
        assert_false(self.Model.queue)
        assert_false(self.Model.queue.active)

    def test_commit_queue_crash(self):
        self.Model.start_queue()
        self.Model._storage[0].update.side_effect = ValueError()
        record = self.enqueue_record()
        record.value = 'error'
        record.save()
        self.Model.remove_one(record)
        self.Model.commit_queue()
        assert_true(self.Model._storage[0].insert.called)
        assert_true(self.Model._storage[0].update.called)
        assert_false(self.Model._storage[0].remove.called)
        assert_false(self.Model.queue)
        assert_false(self.Model.queue.active)

    def test_models_share_null_queue(self):
        model2 = make_model()
        assert_true(self.Model.queue is model2.queue)

    def test_models_share_queue(self):
        model2 = make_model()
        model2.start_queue()
        assert_true(self.Model.queue is model2.queue)
