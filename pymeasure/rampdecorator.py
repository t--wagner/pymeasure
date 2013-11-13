from functools import wraps
from math import ceil
import time
from case import Channel


def RampDecorator(cls):

    # --- Add ramprate property ---
    setattr(cls, '_ramprate', None)

    @property
    def ramprate(self):
        return self._ramprate

    @ramprate.setter
    def ramprate(self, rate):
        self._ramprate = rate

    setattr(cls, 'ramprate', ramprate)

    # --- Add steptime property --- #
    setattr(cls, '_steptime', None)

    @property
    def steptime(self):
        return self._steptime

    @steptime.setter
    def steptime(self, seconds):
        self._steptime = seconds

    setattr(cls, 'steptime', steptime)

    # --- Define the ramp decorator --- #
    def write_decorator(write_method):

        @wraps(write_method)
        def ramp(self, stop, verbose=False):
            start = self.read()[0]

            #Calculate the steps, stepsize and steptime
            try:
                stepsize = abs(self._ramprate * self._steptime)
                steps = int(ceil(abs(stop - start) / stepsize))

                # Correct stepsize and steptime for equal stepping
                stepsize = float(stop - start) / steps
                steptime = abs(stepsize / float(self._ramprate))

            except (TypeError, ZeroDivisionError):
                stepsize = (stop - start)
                steps = 1
                steptime = 0
                

            start_time = time.time()
            last_time = start_time
            position = start
            print position
            print 'hallo'
            for n, step in ((n, start + n * stepsize) for n in xrange(1, steps + 1)):

                position = write_method(self, step)
                

                if verbose:
                    if (time.time() - last_time) > verbose:
                        print position
                        last_time = time.time()

                wait_time = steptime - (time.time() - start_time)
                if wait_time > 0:
                    time.sleep(wait_time)

                start_time = time.time()

            return position

        return ramp

    setattr(cls, 'write', write_decorator(getattr(cls, 'write')))

    return cls


@RampDecorator
class Test(Channel):

    def __init__(self):
        self._factor = 1
        self._val = 0

    def read(self):
        return [self._val / self._factor]

    def write(self, val):
        """Write method

        """

        self._val = val * self._factor
        return self.read()


if __name__ == '__main__':
    t = Test()
    t.ramprate = 10
    t.steptime = 100e-3
