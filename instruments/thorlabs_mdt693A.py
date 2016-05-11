from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelWrite

class Foo:
    def __init__():
        print("foo")


class PiezoControlMDT693AChannel(ChannelWrite):
    
        def __init__(self, instrument, channel, vmax = 150):
            self._instrument = instrument
            self._channel = channel
    
            ChannelWrite.__init__(self)
            self.set_max_voltage(vmax)
            
            
        @ChannelWrite._readmethod
        def read(self):
            command = self._channel + 'R?'
#            return [float(self._instrument.query(self._channel + 'R?')[2:])]
            self._instrument.write(command)
            response = self._instrument.read()
            return [float(response[len(command)+3:-3])]
                                            
        
        @ChannelWrite._writemethod
        def write(self, value):
            if value < 0 or value > 150:
                print("Warning: Voltage is higher than max voltage\n")
            
            self._instrument.write(self._channel + 'V' + str(value))
            return self._instrument.read()
        
        def set_max_voltage(self, value):
            if value < 0 or value > 150:
                print("Warning: Voltage is higher than max voltage\n")
            
            self._instrument.write(self._channel + 'H' + str(value))
            self._instrument.read_raw()
        
        
       
             

class PiezoControlMDT693A(PyVisaInstrument):
    def __init__(self, resource_manager, address, name='', defaults=False, reset=False):
        
        
        PyVisaInstrument.__init__(self, resource_manager, address, name, baud_rate=115200)
        # self.echo_mode()
        self.__setitem__('X', PiezoControlMDT693AChannel(self._instrument, 'X'))
        self.__setitem__('Y', PiezoControlMDT693AChannel(self._instrument, 'Y'))
        self.__setitem__('Z', PiezoControlMDT693AChannel(self._instrument, 'Z'))
        
        # self.__setitem__('Master', PiezoControlMDT693AChannel(self._instrument, 'A'))
        """ This is the master channel, which will write all of the XYZ 
        channels at once """

    def get_information(self):
        """ prints information about the device, such as product header, 
        firmware version etc. """
        self._instrument.write('I')
        return self._instrument.read()[11:-3].replace('\r', '\n')

    def get_information(self):
        """ prints information about the device, such as product header, 
        firmware version etc. """
        self._instrument.write('I')
        return self._instrument.read()[11:-3].replace('\r', '\n')
            
    def write_master_voltage():
        if value < 0 or value > 150:
            print("Warning: Voltage is higher than max voltage\n")
        
        self._instrument.write('AV' + str(value))
        self._instrument.read()
        
    
    def echo_mode(self):
        """ The Device echoes the given command back, probably for testing
        purposes """
        try:
            print(self._instrument.query("E"))
        except visa.VisaIOError:
            print(self._instrument.query("E"))