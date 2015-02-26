# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelWrite
import time
import oxford as ox

class _OxfordIPSFieldChannel(ChannelWrite):

    def __init__(self, instrument):
        ChannelWrite.__init__(self)
        self._instrument = instrument
        self._unit = 'tesla'
        self._readback = True

        self._config += ['rate', 'setpoint', 'sweeprate', 'persistant_field',
                         'heater']

    def __call__(self, *values):
        """ Call the write or read method.

        With optional *values the write method gets called
            x.__call__(*values, **kw) <==> x(*values, **kw) <==>
            x.read(*values, **kw)
        otherwise the read method
            x.__call__(**kw) <==> x(**kw) <==> x.read(**kw)

        """
        if len(values):
            return self.write(*values)
        else:
            return self.read()

    @property
    def setpoint(self):
        return float(ox.write(self._instrument, 'R8'))

    @setpoint.setter
    def setpoint(self, tesla):

        #Set setpoint and verify that the ips got it right
        while True:
            ox.write(self._instrument, 'J' + '%.4f' % (float(tesla)))
            if '%.4f' % (tesla) == '%.4f' % (self.setpoint):
                break

    @property
    def sweeprate(self):
        return float(ox.write(self._instrument, 'R9'))

    @sweeprate.setter
    def sweeprate(self, rate):
        #Set sweeprate and verify that the ips got it right
        while True:
            ox.write(self._instrument, 'T' + '%.4f' % (float(rate)))
            if '%.4f' % (rate) == '%.4f' % (self.sweeprate):
                break

    @property
    def persistant_field(self):
        return float(ox.write(self._instrument, 'R18'))

    # What the heck is a trip field?
    #@property
    #def trip_field(self):
    #    return float(ox.write(self._instrument, 'R19'))

    @property
    def heater(self):
        heater = int(ox.write(self._instrument, 'X')[7:8])

        if heater == 1:
            return True
        elif heater in [0, 2]:
            return False
        else:
            raise ValueError('switch heater fault')

    @heater.setter
    def heater(self, boolean):
        if not (isinstance(boolean, int) and boolean in [0, 1]):
            err_str = 'heater must be bool, int with True = 1 or False = 0.'
            raise ValueError(err_str)

        #Return if heater is already the requested state
        if self.heater == boolean:
            return

        # Turn heater on or off
        if boolean == 0:
            ox.write(self._instrument, 'H0')
        elif boolean == 1:
            ox.write(self._instrument, 'H1')

        # Wait 10seconds to make sure the heater chaged state
        waitingtime = 20
        steptime = 2
        print 'Waiting for heater:',
        while waitingtime:
            print '.',
            waitingtime -= steptime
            time.sleep(steptime)

        #Confirm the heater state
        if self.heater == boolean:
            print boolean
        else:
            print ''
            raise ValueError('switch heater did not change its state.')

    def hold(self):
        ox.write(self._instrument, 'A0')

    def goto_setpoint(self):
        ox.write(self._instrument, 'A1')

    def goto_zero(self):
        ox.write(self._instrument, 'A2')

    def read(self):
        return [float(ox.write(self._instrument, 'R7'))]

    def write(self, tesla, verbose=False):
        if not isinstance(tesla, (int, float)):
            raise ValueError

        # Set setpoint
        self.setpoint = tesla

        # Go to set point
        self.goto_setpoint()

        last_time = time.time()
        # Wait until the oxford stops sweeping
        while int(ox.write(self._instrument, 'X')[10:11]):

            if verbose:
                if (time.time() - last_time) > verbose:
                    last_time = time.time()
                    print self.read()

        # Put on hold
        self.hold()

        # Return the field
        if self._readback:

            # Two avoid wrong values from the ips we need to compare two
            # readbacks.
            condition = 1
            last_value = None
            while condition:
                value = self.read()
                if last_value == value:
                    condition -= 1
                else:
                    condition = 1
                last_value = value

            return value
        else:
            return [tesla]


class QxfordIPS(PyVisaInstrument):

    def __init__(self, rm, address, name='', reset=True, defaults=True):
        PyVisaInstrument.__init__(self, rm, address, name)
        self._instrument.read_termination = self._instrument.CR

        # Set the communication protocol to normal
        #ox.write(self._instrument, 'Q0')

        # Channels
        self.__setitem__('bfield', _OxfordIPSFieldChannel(self._instrument))

        if defaults is True:
            self.defaults()

    #@property
    #def status(self):
    #    return self._instrument.query('X')

    def defaults(self):
        pass

