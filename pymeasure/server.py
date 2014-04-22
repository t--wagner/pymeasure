import multiprocessing as mp
import time


class Server(mp.Process):

    def __init__(self):
        mp.Process.__init__(self)
        self._task = mp.Queue()
        self._hold = mp.Event()

    def hold(self):
        self._hold.set()

    def query(self, query):
        self._task.put(query)

    def run(self):
        while not self._hold.is_set():
            while not self._task.empty():
                task = self._task.get(False)
                print task

if __name__ == '__main__':
    p = Server()
    p.start()
    p.query('hallo')
    p.query('du arsch')
    p.query('loch!!!')
    time.sleep(1)
    p.hold()
