import time


class LinearSweep(object):

    def __init__(self, channel, start, stop, points):
        self._channel = channel
        self._start = start
        self._stop = stop
        self._points = points

    def __iter__(self):
        for step in self.steps:
            yield self._channel.write(step)

    def __len__(self):
        return self.points

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

    def __init__(self, time, points):

        self._time = time
        self._points = int(points)

    def __iter__(self):
        for step in xrange(self._points):
            time.sleep(self._time)
            yield step

    def __len__(self):
        return self._points

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        self._points = points
