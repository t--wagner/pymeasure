import time


class LinearSweep(object):

    def __init__(self, channels, start, stop, points):
        if isinstance(channels, (list, tuple)):
            self._channels = channels
        else:
            self._channels = [channels]

        self._start = start
        self._stop = stop
        self._points = points

    def __iter__(self):
        for step in self.steps:
            step_list = []
            for channel in self._channels:
                step_list += channel.write(step)
            yield step_list

    @property
    def steps(self):
        return [self.stepsize * n + self._start for n in xrange(self._points)]

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self._start = start

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, stop):
        self._stop = stop

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        if type(points) is int:
            self._points = points
        else:
            raise ValueError

    @property
    def stepsize(self):
        return (self._stop - self._start) / float(self._points - 1)

    @stepsize.setter
    def stepsize(self, stepsize):
        self._points = int(float((self._stop) - self._start) / stepsize) + 1


class TimeSweep(object):

    def __init__(self, seconds, points):

        self._waitingtime = seconds
        self._points = int(points)

    def __iter__(self):
        for step in xrange(self._points):
            time.sleep(self._waitingtime)
            yield step

    @property
    def waitingtime(self):
        return self._waitingtime

    @waitingtime.setter
    def waitingtime(self, seconds):
        self._waitingtime = seconds

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        self._points = points
