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

        try:
            answer = self._function(*self._args, **self._kwargs)
        except Exception, exception:
            answer = TaskError(repr(exception))

        self._answer.put(answer)


class Server(Process):

    def __init__(self, manager=None):
        """Create and initialize attributes.

        """

        Process.__init__(self)

        if not manager:
            manager = Manager()

        self._manager = manager
        self._tasks = Queue()
        self._stop = Event()

    def stop(self):
        """Stop the running server.

        """

        self._stop.set()

    def add_task(self, function, *args, **kwargs):
        """Add a new task.

        """

        #if not isinstance(task, Task):
        #    raise TypeError('not a Task.')

        if self._stop.is_set():
            raise ValueError('Server stopped.')

        result = self._manager.Queue()
        task = Task(function, result, *args, **kwargs)
        self._tasks.put(task)

        return Answer(result)

    def run(self):
        """Code to be executed when start is called.

        """

        while True:
            # Process all tasks in the queue
            while not self._tasks.empty():
                task = self._tasks.get()
                task()

            # Stop server if requested
            if self._stop.is_set():
                return


if __name__ == '__main__':

    def pot(val):
        return val**2

    # Create nd start server
    p = Server()
    p.start()
    q0 = p.add_task(pot, 2)
    q1 = p.add_task(pot, 'a')
    q2 = p.add_task(pot, 8)
    print q0.get()
    print q1.get()
    print q2.get()
    p.stop()
