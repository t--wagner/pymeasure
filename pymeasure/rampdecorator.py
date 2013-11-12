import time
from functools import wraps

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
    def write_decorator(write):

        @wraps(write)
        def ramp(self, stop, verbose=False):
            start = self.read()[0]
            position = start

            try:
                stepsize = abs(self._steptime * self._ramprate * self._factor)
            except TypeError:
                stepsize = None

            #Calculate number of points
            try:
                points = abs(int(float(stop - start) / stepsize)) + 1
            except TypeError:
                points = 1

            #Correction of stepsize
            stepsize = float(stop - start) / points

            #Correction of steptime
            try:
                steptime = abs(stepsize / float(self._ramprate * self._factor))
            except TypeError:
                steptime = 0

            start_time = time.time()
            for n, step in ((n, start + n * stepsize) for n in xrange(1, points + 1)):
                #print "step: " + str(step)
                position = write(self, step)
                if verbose:
                    print position

                wait_time = steptime - (time.time() - start_time)
                if wait_time > 0:
                    time.sleep(wait_time)

                start_time = time.time()

                try:
                    pass
                except KeyboardInterrupt:
                    break

            return position

        return ramp

    setattr(cls, 'write', write_decorator(getattr(cls, 'write')))

    return cls


@RampDecorator
class Test(object):

    def __init__(self):
        self._factor = 1
        self._val = 0

    def read(self):
        return [self._val]


    def write(self, val):
        """Write method

        """

        self._val = val
        return self.read()


if __name__ == '__main__':
    t = Test()
    t.ramprate = 10
    t.steptime = 100e-3
