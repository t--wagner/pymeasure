from pyvisa_instrument import PyVisaInstrument
from ..pymeasure import Channel, Ramp


class _Egg7260LockInAmplifierChannel(Channel):
    
    def __init__(self, pyvisa_instr, channel):
        Channel.__init__(self)
        self._pyvisa_instr = pyvisa_instr
        self._channel = channel
        self._factor = 1
           
    def read(self):
        level =  self._pyvisa_instr.ask_for_values(self._channel + ".")        
        return [level[0] / float(self._factor)]


class _Egg7260LockInAmplifierOscillator(Channel, Ramp):

    def __init__(self, pyvisa_instr):
        Channel.__init__(self)
        self._pyvisa_instr = pyvisa_instr
        self._unit = 'volt'
        self._factor = 1
        self._readback = True
        
        Ramp.__init__(self)
        self.write = Ramp._rampdecorator(self, self.read, self.write, self._factor)

    #--- factor ---#        
    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, factor):
        self._factor = factor

    #--- readback ---#
    @property
    def readback(self):
        return self._readback

    @readback.setter
    def readback(self, readback):
        self._readback = readback
    
    @property
    def frequency(self):
        return self._pyvisa_instr.ask_for_values('OF.')        
        
    @frequency.setter
    def frequency(self, frequency):
        self._pyvisa_instr.write('OF. ' + str(frequency))
    
    def read(self):
        return self._pyvisa_instr.ask_for_values('OA.')
    
    def write(self, level):
        self._pyvisa_instr.write('OA. ' + str(level))

        if self._readback:
            return self.read()
        else:
            return [level]

class Egg7260LockInAmplifier(PyVisaInstrument):

    def __init__(self, name, address, defaults=True):
        PyVisaInstrument.__init__(self, address)
        
        # Channels
        self.__setitem__('X', _Egg7260LockInAmplifierChannel(self._pyvisa_instr, 'X'))
        self.__setitem__('Y', _Egg7260LockInAmplifierChannel(self._pyvisa_instr, 'Y'))
        self.__setitem__('R', _Egg7260LockInAmplifierChannel(self._pyvisa_instr, 'MAG'))
        self.__setitem__('Phase', _Egg7260LockInAmplifierChannel(self._pyvisa_instr, 'PHA'))
        self.__setitem__('Oscillator', _Egg7260LockInAmplifierOscillator(self._pyvisa_instr))

        if defaults is True:
            self.defaults()   
    
    def defaults(self):
        pass
    
    @property
    def identification(self):
        return 'EG&G DSP Lock-in Amplifier Model ' + self._pyvisa_instr.ask("ID")