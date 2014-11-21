# -*- coding: utf-8 -*

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelWrite
import time
from visa import VisaIOError


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

    def _send_command(self, cmd_string):
        while True:

            # Sending '\r' before every command makes the communication very
            # stabel and is strongly recommendanded by Timo (after an entire
            # weekend of fighting with the fucking ips)
            self._instrument.query('')
            answer = self._instrument.query(cmd_string)

            try:
                # The ips answers with the commands first letter if it
                # understood otherwise with '?'
                if answer[0] == cmd_string[0]:
                    return answer[1:]
            except IndexError:
                # Once in a while IndexErrors occur if a previous command got
                # interrupted.

                #print '----- IndexError ----'
                #print cmd_string
                #print answer
                #print '---------------------'

                timeout = self._instrument.timeout
                self._instrument.timeout = 1
                try:
                    self._instrument.read()
                except VisaIOError:
                    pass
                self._instrument.timeout = timeout

    @property
    def setpoint(self):
        return float(self._send_command('R8'))

    @setpoint.setter
    def setpoint(self, tesla):

        #Set setpoint and verify that the ips got it right
        while True:
            self._send_command('J' + '%.4f' % (float(tesla)))
            if '%.4f' % (tesla) == '%.4f' % (self.setpoint):
                break

    @property
    def sweeprate(self):
        return float(self._send_command('R9'))

    @sweeprate.setter
    def sweeprate(self, rate):
        #Set sweeprate and verify that the ips got it right
        while True:
            self._send_command('T' + '%.4f' % (float(rate)))
            if '%.4f' % (rate) == '%.4f' % (self.sweeprate):
                break

    @property
    def persistant_field(self):
        return float(self._send_command('R18'))

    # What the heck is a trip field?
    #@property
    #def trip_field(self):
    #    return float(self._send_command('R19'))

    @property
    def heater(self):
        heater = int(self._send_command('X')[7:8])

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
            self._send_command('H0')
        elif boolean == 1:
            self._send_command('H1')

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
        self._send_command('A0')

    def goto_setpoint(self):
        self._send_command('A1')

    def goto_zero(self):
        self._send_command('A2')

    def read(self):
        return [float(self._send_command('R7'))]

    def write(self, tesla, verbose=False):
        if not isinstance(tesla, (int, float)):
            raise ValueError

        # Set setpoint
        self.setpoint = tesla

        # Go to set point
        self.goto_setpoint()

        last_time = time.time()
        # Wait until the oxford stops sweeping
        while int(self._send_command('X')[10:11]):

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

        # Channels
        self.__setitem__('bfield', _OxfordIPSFieldChannel(self._instrument))

        if defaults is True:
            self.defaults()

    #@property
    #def status(self):
    #    return self._instrument.query('X')

    def defaults(self):
        pass

