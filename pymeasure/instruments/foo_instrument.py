import numpy as np
from ..case import Channel, Instrument
import random


class FooDriver(object):

        def __init__(self):
                self._values = []
        
        def measure(self, measf):
            product = 1
            for value in self._values:
                product *= value
            return measf(product)

        def source(self, port, value=None):
            if value is None:
                return self._values[port]
            else: 
                self._values[port] = value
                return value


class FooChannelMeas(Channel):
    
    def __init__(self, driver, measf):
        super(FooChannelMeas, self).__init__()
        self._driver = driver
        self._measf = measf
        
    def read(self):
        return [self._driver.measure(self._measf)]


class FooChannelSin(FooChannelMeas):
    
    def __init__(self, driver):
        super(FooChannelSin, self).__init__(driver, np.sin)
        
    def read(self):
        """ Hallo hier gibt es den Sin """
        return super(FooChannelSin, self).read()


class FooChannelCos(FooChannelMeas):
        
    def __init__(self, driver):
        super(FooChannelCos, self).__init__(driver, np.cos)
        
    def read(self):
        """ Hallo hier gibt es den Cos """
        return super(FooChannelCos, self).read()

    
class FooChannelSource(Channel):
    
    def __init__(self, driver, port):
        super(FooChannelSource, self).__init__()
        
        self._driver = driver
        self._port = port
        self._driver._values.append(0)
        
        #Ramp.__init__(self)
        #self.write = self._rampdecorator(self.read, self.write)
        
    def read(self):
        return [self._driver.source(self._port)]
        
    def write(self, value):
        return [self._driver.source(self._port, value)]
        
  
class FooChannelPort0(FooChannelSource):
    
    def __init__(self, driver):
        super(FooChannelPort0, self).__init__(driver, 0)
        
    def read(self):
        """ Hier bekommst den Level von Port 0 """
        return super(FooChannelPort0, self).read()
        
    def write(self, value):
        """ Hier kannst den Level von Port 0 setzen """
        return super(FooChannelPort0, self).write(value)
       
        
class FooChannelPort1(FooChannelSource):
    
    def __init__(self, driver):
        super(FooChannelPort1, self).__init__(driver, 1)
        
    def read(self):
        """ Hier bekommst den Level von Port 1 """
        return super(FooChannelPort1, self).read()
        
    def write(self, value):
        """ Hier kannst den Level von Port 1 setzen """
        return super(FooChannelPort1, self).write(value)


class FooChannelRandom(Channel):
    
    def __init__(self):
        pass
    
    def read(self):
        return [random.uniform(-1, 1)]
        

class FooInstrument(Instrument):

    def __init__(self, reset=True):
        super(FooInstrument, self).__init__()
        
        self._driver = FooDriver()
        
        self.__setitem__('source0', FooChannelPort0(self._driver))   
        self.__setitem__('source1', FooChannelPort1(self._driver))
        
        self.__setitem__('sin', FooChannelSin(self._driver))
        self.__setitem__('cos', FooChannelCos(self._driver))
        self.__setitem__('random', FooChannelRandom())
        
        if reset is True:
            self.reset()
        
    def reset(self):
        pass
        #self.__getitem__('source0').steptime = 10e-3
        #self.__getitem__('source1').steptime = 10e-3
        