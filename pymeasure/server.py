from multiprocessing import Process, Queue, Manager


class Server(Process):

    def __init__(self):
        """Create and initialize attributes.

        """

        # Init multprocessing.Process
        Process.__init__(self)

        self._manger = Manager()
        self._calls = Queue()
        self._instrument = dict()

    def connect(self, key, instrument):
        self._instrument[key] = instrument
        return Transmitter(self._manger, key, self._calls)

    def stop(self):
        """Stop the running server.

        """

        # Send poison pill
        self._calls.put(None)

    def run(self):
        """Code to be executed when start is called.

        """

        while True:
            # Get next task in queue
            call = self._calls.get()

            # Look for poison pill
            if call is None:
                return

            try:
                #Process the task
                key, val, answer = call
                instrument = self._instrument[key]
                val = instrument.ask(val)
                answer.put(val)
            except Exception, exception:
                print repr(exception)


class Transmitter(object):

    def __init__(self, manager, key, question):
        self._manger = manager
        self._key = key
        self._question = question

    def ask(self, string):
        answer = self._manger.Queue()
        self._question.put([self._key, string, answer])
        return answer
    

class VirtualDevice(object):
    
    def ask(self, val):
        return val

    def write(self, val):
        pass


if __name__ == '__main__':

    # Create and start server
    m = Manager()
    s = Server()
    c1 = s.connect('v0', VirtualDevice())
    c0 = s.connect('v1', VirtualDevice())

    s.start()
    a = c0.ask('hallo')
    b = c0.ask('du')
    print b.get()
    print b.get()
    
    s.stop()
