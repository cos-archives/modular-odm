import copy
import logging


logger = logging.getLogger(__name__)


class WriteAction(object):

    def __init__(self, method, *args, **kwargs):
        if not callable(method):
            raise TypeError('Argument `method` must be callable')
        self.method = method
        self.args = copy.deepcopy(args)
        self.kwargs = copy.deepcopy(kwargs)

    def execute(self):
        return self.method(*self.args, **self.kwargs)


class WriteQueue(object):

    def __init__(self):
        self.active = False
        self.actions = []

    def start(self):
        if self.active:
            logger.warn('Already working in a write queue. Further writes '
                        'will be appended to the current queue.')
        self.active = True

    def push(self, action):
        if not self.active:
            raise ValueError('Cannot push unless queue is active')
        if not isinstance(action, WriteAction):
            raise TypeError('Argument `action` must be instance '
                            'of `WriteAction`')
        self.actions.append(action)

    def commit(self):
        if not self.active:
            raise ValueError('Cannot commit unless queue is active')
        results = []
        while self.actions:
            action = self.actions.pop(0)
            results.append(action.execute())
        return results

    def clear(self):
        self.active = False
        self.actions = []

    def __nonzero__(self):
        return bool(self.actions)


class QueueContext(object):

    def __init__(self, cls):
        self.cls = cls

    def __enter__(self):
        self.cls.start_queue()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cls.commit_queue()
