# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 13:40:16 2015

@author: kuehne
"""

from pymeasure.instruments.pyvisa_instrument import PyVisaInstrument
from pymeasure.case import ChannelRead, ChannelStep
import time
import numpy as np
from visa import VisaIOError


class TransferFunction(ChannelRead):

    def __init__(self, instrument):
        self._instrument = instrument
        ChannelRead.__init__(self)

        self._config += []

    @ChannelRead._readmethod
    def read(self):
        bins = int(self._instrument.query('DSPN? 1'))
        noise = []
        for i in range(bins):
            noise += [float(self._instrument.query('DSPY? 1, {}'.format(i)))]
            return noise

    @property
    def get_frequency(self):
        bins = int(self._instrument.query('DSPN? {}'.format(self._channel)))
        start = float(self._instrument.query('FSTR? {}'.format(self._channel)))
        end = float(self._instrument.query('FEND? {}'.format(self._channel)))
        freq = np.linspace(int(start), int(end), int(bins))
        return freq 

    @property
    def resolution(self):
        bins = int(self._instrument.query('FLIN? 1'))
        values = [101, 201, 401, 801]
        return values[bins]

    @resolution.setter
    def resolution(self, bins):
        if bins < 150:
            number = 0
        elif bins < 250:
            number = 1
        elif bins < 600:
            number = 2
        else:
            number = 3 
        self._instrument.write('FLIN2 , {}'.format(number))

    @property
    def range(self):
        start = float(self._instrument.query('FSTR? 1'))
        end = float(self._instrument.query('FEND? 1'))
        return [start, end]

    @range.setter
    def range(self, frange):
        span = int(frange[1] - frange[0])
        self._instrument.write('FSPN 2,{}'.format(span))
        self._instrument.write('FEND 2,{}'.format(int(frange[1])))
        self._instrument.write('FSTR 2,{}'.format(int(frange[0])))

    @property
    def average_complete(self):
        avpoints1 = int(self._instrument.query('FAVN? 0'))
        finished1 = int(self._instrument.query('NAVG? 0'))
        avpoints2 = int(self._instrument.query('FAVN? 1'))
        finished2 = int(self._instrument.query('NAVG? 1'))
        return avpoints1 == finished1 and avpoints2 == finished2

    @property
    def averagepoints(self):
        avpoints = int(self._instrument.query('FAVN? 1'))
        return avpoints

    @averagepoints.setter
    def averagepoints(self, avpoints):
        self._instrument.write('FAVN2, {}'.format(avpoints))

    @property
    def autoscale(self):
        self._instrument.write('ASCL 0')
        self._instrument.write('ASCL 1')


class Source(ChannelStep):

    def __init__(self, instrument, channel):
        self._instrument = instrument
        self._channel = channel
        self._source = int(self._instrument.query('STYP?'))

        ChannelStep.__init__(self)
        self.unit = 'Hz'

    @ChannelStep._readmethod
    def read(self):
        if self._source == 0:
            if self._channel == 1:
                sourcefreq = self._instrument.query_ascii_values('S2FR?')
                return sourcefreq
            elif self._channel == 0:
                sourcefreq = self._instrument.query_ascii_values('S1FR?')
                return sourcefreq
        elif self._source == 1:
            burst = self._instrument.query_ascii_values('CBUR?')
            return burst
        elif self._source == 2:
            burst = self._instrument.query_ascii_values('NBUR?')
            return burst

    @ChannelStep._writemethod
    def write(self, freq):
        if self._source == 0:
            if self._channel == 0:
                self._instrument.write('S1FR {}'.format(int(freq)))
            elif self._channel == 1:
                self._instrument.write('S2FR {}'.format(int(freq)))
        elif self._source == 1:
            if freq > 100 or freq < 0:
                raise ValueError('number has to be between 0 and 100')
            else:
                self._instrument.write('CBUR {}.'.format(int(freq)))
        elif self._source == 2:
            if freq > 100 or freq < 0:
                raise ValueError('number has to be between 0 and 100')
            else:
                self._instrument.write('NBUR {}.'.format(int(freq)))

    @property
    def source_type(self):
        source = int(self._instrument.query('STYP?'))
        sourcelist = ['Sine', 'Chirp', 'Noise', 'Arbitrary']
        return sourcelist[source]

    @source_type.setter
    def source_type(self, source):
        """Source type has to be an integer of range(4)
        [0,1,2,3] = ['Sine', 'Chirp', 'Noise', 'Arbitrary']
        """
        self._instrument.write('STYP {}'.format(int(source)))

    @property
    def amplitude(self):
        if self._source == 0:
            if self._channel == 0:
                amplitude = float(self._instrument.query('S1AM?'))
            elif self._channel == 1:
                amplitude = float(self._instrument.query('S2AM?'))
            return amplitude
        elif self._source == 1:
            amplitude = float(self._instrument.query('CAMP?'))
            return amplitude
        elif self._source == 2:
            amplitude = float(self._instrument.query('NAMP?'))
            return amplitude

    @amplitude.setter
    def amplitude(self, amplitude):
        if self._source == 0:
            if self._channel == 0:
                self._instrument.write('S1AM {}'.format(float(amplitude)))
            elif self._channel == 1:
                self._instrument.write('S2AM {}'.format(float(amplitude)))
        elif self._source == 1:
            self._instrument.write('CAMP {}'.format(float(amplitude)))
        elif self._source == 2:
            self._instrument.write('NAMP {}'.format(float(amplitude)))

    @property
    def offset(self):
        if self._source == 0:
            offset = float(self._instrument.query('SOFF?'))
            return offset
        else:
            raise SystemError('offset is not defined for this source type')

    @offset.setter
    def offset(self, offset):
        if self._source == 0:
            self._instrument.write('SOFF {}'.format(int(offset)))
        else:
            raise SystemError('offset is not defined for this source type')

    @property
    def noise_type(self):
        if self._source == 2:
            noiselist = ['Bandlimited White', 'White', 'Pink']
            noise = int(self._instrument.query_ascii_values('NTYP?'))
            return noiselist[noise]
        else:
            raise SystemError('only available for source type = noise')

    @noise_type.setter
    def noise_type(self, noise):
        if self._source == 2:
            """Noise type has to be an integer of range(3)
            [0,1,2] = ['Bandlimited White', 'White', 'Pink']
            """
            self._instrument.write('NTYP {}'.format(int(noise)))
        else:
            raise SystemError('only available for source type = noise')


class Spectrum(ChannelRead):

    def __init__(self, instrument, channel):
        self._instrument = instrument
        self._channel = channel
        ChannelRead.__init__(self)

        self._config += []

#    fast but not stable for high resolution and/or for some units
#    @ChannelRead._readmethod
#    def read(self):
#        if self._channel == 2:
#            return 'error: can only read one channel at once'
#        else:
#            noise = self._instrument.query_ascii_values('DSPY? {}'.format(self._channel))            
#            return noise

    @ChannelRead._readmethod
    def read(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            bins = int(self._instrument.query('DSPN? {}'.format(self._channel)))
            noise = []
            for i in range(bins):
                noise += [float(self._instrument.query('DSPY? {}, {}'.format(self._channel, i)))]
                #noise += [self._instrument.query_binary_values('DSPB? {}, {}'.format(self._channel,i), datatype = 'f')]
            return noise


#    @ChannelRead._readmethod
#    def read(self):
#        if self._channel == 2:
#            raise SystemError('can only read one channel at once')
#        else:
#            noise = self._instrument.query_binary_values('DSPB ? {}'.format(self._channel), datatype='f', is_big_endian=True)
#            return noise
            
#    @property
#    def get_frequency(self):
#        if self._channel == 2:
#            return 'error: can only read one channel at once'
#        else:
#            bins = int(self._instrument.query('DSPN? {}'.format(self._channel))) 
#            frequency = []
#            for i in range(bins):
#                frequency += [float(self._instrument.query('DBIN? {},{}'.format(self._channel,i)))]     
#            return frequency

    @property
    def get_frequency(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            bins = int(self._instrument.query('DSPN? {}'.format(self._channel)))
            start = float(self._instrument.query('FSTR? {}'.format(self._channel)))
            end = float(self._instrument.query('FEND? {}'.format(self._channel)))
            freq = np.linspace(int(start), int(end), int(bins))
            return freq 
            
    @property
    def read_binary(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            bins = int(self._instrument.query('DSPN? {}'.format(self._channel)))
            self._instrument.read_termination = None
            time.sleep(0.2)
            while True:
                try:
                        noise = self._instrument.query_binary_values('DSPB? {}'.format(self._channel),  header_fmt='empty')
                        if bins != len(noise):
                            pass
                        self._instrument.read_termination = self._instrument.LF                        
                        break
                except (VisaIOError, IndexError):
                        noise = []
                        pass
            
            
            #self._instrument.read_termination = self._instrument.LF
            #time.sleep(0.2)
            #self._instrument.write('*CLS')
            return noise

    @property
    def resolution(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            bins = int(self._instrument.query('FLIN? {}'.format(self._channel)))

            values = [101, 201, 401, 801]
            return values[bins]

    @resolution.setter
    def resolution(self, bins):
        if bins < 150:
            number = 0
        elif bins < 250:
            number = 1
        elif bins < 600:
            number = 2
        else:
            number = 3
        self._instrument.write('FLIN {} , {}'.format(self._channel, number))

    @property
    def frequency_span(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            span = float(self._instrument.query('FSPN? {}'.format(self._channel)))
            return span

    @frequency_span.setter
    def frequency_span(self, span):
        self._instrument.write('FSPN {},{}'.format(self._channel, span))

    @property
    def range(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            start = float(self._instrument.query('FSTR? {}'.format(self._channel)))
            end = float(self._instrument.query('FEND? {}'.format(self._channel)))
            return [start, end]

    @range.setter
    def range(self, frange):
        span = int(frange[1] - frange[0])
        self._instrument.write('FSPN {},{}'.format(self._channel, span))
        self._instrument.write('FEND {},{}'.format(self._channel, int(frange[1])))
        self._instrument.write('FSTR {},{}'.format(self._channel, int(frange[0])))

    @property
    def averagepoints(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            avpoints = int(self._instrument.query('FAVN? {}'.format(self._channel)))
            return avpoints

    @averagepoints.setter
    def averagepoints(self, avpoints):
        self._instrument.write('FAVN {} , {}'.format(self._channel, avpoints))

    @property
    def average_complete(self):
        if self._channel ==2:
            avpoints1 = int(self._instrument.query('FAVN? 0'))
            finished1 = int(self._instrument.query('NAVG? 0'))
            avpoints2 = int(self._instrument.query('FAVN? 1'))
            finished2 = int(self._instrument.query('NAVG? 1'))
            return avpoints1 == finished1 and avpoints2 == finished2
        else:
            avpoints = int(self._instrument.query('FAVN? {}'.format(self._channel)))
            finished = int(self._instrument.query('NAVG? {}'.format(self._channel)))
            return avpoints == finished

    @property
    def autoscale(self):
        if self._channel == 2:
            self._instrument.write('ASCL 0')
            self._instrument.write('ASCL 1')
        else:
            self._instrument.write('ASCL {}'.format(self._channel))

    @property
    def autoranging(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        elif self._channel == 1:
            boolian = int(self._instrument.query('A2RG?'))
            return bool(boolian)
        elif self._channel == 0:
            boolian = int(self._instrument.query('A1RG?'))
            return bool(boolian)

    @autoranging.setter
    def autoranging(self, boolian):
        boolian = int(boolian)
        if self._channel == 2:
            self._instrument.write('A1RG {}'.format(boolian))
            self._instrument.write('A2RG {}'.format(boolian))
        elif self._channel == 1:
            self._instrument.write('A2RG {}'.format(boolian))
        elif self._channel == 0:
            self._instrument.write('A1RG {}'.format(boolian))

    @property
    def auto_offset(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            boolian = int(self._instrument.query('IAOM?'))
            return bool(boolian)

    @auto_offset.setter
    def auto_offset(self, boolian):
        boolian = int(boolian)
        self._instrument.write('IAOM {}'.format(boolian))

    @property
    def unit_set(self):
        """Chosen unit has to be an integer of range(6)
        [0,1,2,3,4,5] = ['Vpk', 'Vrms', 'Vpk^2', 'Vrms^2', 'dBVpk', 'dBVrms']
        """
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            unit = int(self._instrument.query('UNIT? {}'.format(self._channel)))
            unitlist = ['Vpk', 'Vrms', 'Vpk^2', 'Vrms^2', 'dBVpk', 'dBVrms']
            return unitlist[unit]

    @unit_set.setter
    def unit_set(self, unit):
        """Chosen unit has to be an integer of range(6)
        [0,1,2,3,4,5] = ['Vpk', 'Vrms', 'Vpk^2', 'Vrms^2', 'dBVpk', 'dBVrms']
        """
        self._instrument.write('UNIT {}, {}'.format(self._channel, int(unit)))



class SweptSine(ChannelRead):

    def __init__(self, instrument, channel):
        self._instrument = instrument
        self._channel = channel
        ChannelRead.__init__(self)

        self._config += []

    @ChannelRead._readmethod
    def read(self):
        bins = int(self._instrument.query('DSPN? {}'.format(self._channel)))
        noise = []
        for i in range(bins):
            noise += [float(self._instrument.query('DSPY? {}, {}'.format(self._channel, i)))]            
        return noise

    @property
    def get_frequency(self):
        bins = int(self._instrument.query('DSPN? {}'.format(self._channel)))
        start = float(self._instrument.query('SSTR? {}'.format(self._channel)))
        end = float(self._instrument.query('SSTP? {}'.format(self._channel)))
        freq = np.linspace(int(start), int(end), int(bins))
        return freq 

    @property
    def range(self):
        start = float(self._instrument.query('SSTR? {}'.format(self._channel)))
        end = float(self._instrument.query('SSTP? {}'.format(self._channel)))
        return [start,end]

    @range.setter
    def range(self, frange):
        self._instrument.write('SSTP {},{}'.format(self._channel, int(frange[1])))
        self._instrument.write('SSTR {},{}'.format(self._channel, int(frange[0])))

    @property
    def resolution(self):
        bins = self._instrument.query('SNPS? {}'.format(self._channel))
        return int(bins)

    @resolution.setter
    def resolution(self, bins):
        self._instrument.write('SNPS{}, {}'.format(self._channel, int(bins)))

    @property
    def autoscale(self):
        if self._channel == 2:
            self._instrument.write('ASCL 0')
            self._instrument.write('ASCL 1')
        else:
            self._instrument.write('ASCL {}'.format(self._channel))

    @property
    def auto_offset(self):
        if self._channel == 2:
            raise SystemError('can only read one channel at once')
        else:
            boolian = int(self._instrument.query('IAOM?'))
            return bool(boolian)

    @auto_offset.setter
    def auto_offset(self, boolian):
        boolian = int(boolian)
        self._instrument.write('IAOM {}'.format(boolian))


class SR780(PyVisaInstrument):
    def __init__(self, rm, address, name=''):
        PyVisaInstrument.__init__(self, rm, address, name)

        self._instrument.read_termination = self._instrument.LF
        self._instrument.write_termination = self._instrument.LF
        #self._instrument.timeout = 4000

        self._instrument.write('*CLS')
        self._instrument.write('OUTX0')
        self._instrument.write('ALRM 0')
        self._instrument.write('AOVL 0')

        self.__setitem__('spectrum1', Spectrum(self._instrument, 0))
        self.__setitem__('spectrum2', Spectrum(self._instrument, 1))
        self.__setitem__('both', Spectrum(self._instrument, 2))
        self.__setitem__('transferfunction', TransferFunction(self._instrument))
        self.__setitem__('sweptsine1', SweptSine(self._instrument, 0))
        self.__setitem__('sweptsine2', SweptSine(self._instrument, 1))
        self.__setitem__('sinesource1', Source(self._instrument, 0))
        self.__setitem__('sinesource2', Source(self._instrument, 1))



    def reset(self):
        self._instrument.write("*RST")
        time.sleep(15)
        self._instrument.write('*CLS')
        self._instrument.write('OUTX0')
        self._instrument.write('MGRP2, 0')      #FFT measurement
        self._instrument.write('ALRM 0')
        self._instrument.write('AOVL 0')

    def start_average(self):
        self._instrument.write('FAVG 2, 1')     #averaging is on (both displays)
        self._instrument.write('FAVT 2, 0')     #average type is linear  
        self._instrument.write('STRT')          #starts new averaging

    def TransferFunction(self):
        self._instrument.write('MGRP2, 0')
        self._instrument.write('MEAS0, 0')
        self._instrument.write('MEAS1, 10')
        self._instrument.write('VIEW2, 1')
        self._instrument.write('UNIT1, 10')
        self._instrument.write('UNIT0, 3')
        self._instrument.write('FWIN2, 0')
        self._instrument.write('SRCO 1')        #Sourcing is on
        self._instrument.write('STYP 1')
        self._instrument.write('CSRC 0')

    def SweptSine(self):
        self._instrument.write('MGRP2, 2')
        self._instrument.write('MEAS0, 30')
        self._instrument.write('MEAS1, 31')
        self._instrument.write('VIEW2, 1')
        self._instrument.write('UNIT2, 3')
        self._instrument.write('FWIN2, 3')
        self._instrument.write('IAOM 0')    #turn off auto offset
        self._instrument.write('FAVM2, 0')
        self._instrument.write('SSTY2, 0')

    def FFT(self):
        self._instrument.write('MGRP2, 0')
        self._instrument.write('MEAS0, 0')
        self._instrument.write('MEAS1, 1')
        self._instrument.write('VIEW2, 2')
        self._instrument.write('UNIT2, 3')
        self._instrument.write('FWIN2, 1')  #Hanning Filter is used
        self._instrument.write('IAOM 0')    #turn off auto offset
        self._instrument.write('FAVM2, 1')

    @property
    def sourcing(self):
        boolian = int(self._instrument.query('SRCO?'))      #ask if source is on or of
        boolian2 = int(self._instrument.query('STYP?'))     #ask for source type 
        return bool(boolian) and not bool(boolian2)

    @sourcing.setter
    def sourcing(self, boolian):
        self._instrument.write('SRCO {}'.format(int(boolian)))
        if boolian == True:
            self._instrument.write('STYP 0')

    @property
    def identification(self):
        return self._instrument.query("*IDN?")

if __name__ == '__main__':
    sr = SR780(rm, 'GPIB0::10::INSTR')
