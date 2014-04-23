from multiprocessing import Process, Manager, Queue, Event
import time


class TaskError(object):
    def __init__(self, message):
        self.message = message

class Answer(object):

    def __init__(self, queue):
        self._queue = queue

    def get(self):
        answer = self._queue.get()

        # Look for Errors
        if isinstance(answer, TaskError):
            raise Exception(answer.message)

        return answer


class Task(object):

    def __init__(self, function, answer, *args, **kwargs):
        """Create and initialize attributes.

        """

        self._function = function
        self._answer = answer
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        """Call the function.

        """

        answer = self._function(*self._args, **self._kwargs)
        self._answer.put(answer)


class ConnectionBase(object):

    def __init__(self, server):
        self._server = server

    def ask(self, function):

        q = self._server.add_task(function, 2)
        return q


class Server(Process):

    def __init__(self, manager=None):
        """Create and initialize attributes.

        """

        # Init multprocessing.Process
        Process.__init__(self)

        # Create multiprocessing.Manger
        if not manager:
            manager = Manager()
        self._manager = manager

        self._tasks = Queue()
        self._connections = dict()

    def stop(self):
        """Stop the running server.

        """

        self._tasks.put('MSG:STOP_SERVER')

    def add_task(self, function, *args, **kwargs):
        """Add a new task.

        """

        answer = self._manager.Queue()
        task = Task(function, answer, *args, **kwargs)
        self._tasks.put(task)

        return Answer(answer)

    def run(self):
        """Code to be executed when start is called.

        """

        while True:
            # Process all tasks in the queue
            task = self._tasks.get()
            try:
                task()
            except Exception, exception:
                if isinstance(task, str):
                    if task == 'MSG:STOP_SERVER':
                        return

                #self._tasks._answer.put(TaskError(repr(exception)))


if __name__ == '__main__':

    def pot(val):
        return val**2

    # Create nd start server
    p = Server()
    p.start()
    q = p.add_task(pot, 2)
    print q.get()
    #p.stop()
