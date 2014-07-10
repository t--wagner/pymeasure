# -*- coding: utf-8 -*-

import random
import pymeasure as pym


def readchannel_test(channel):

    print 'Test read method:'
    print ''

    # Channel information
    print channel
    print ''

    print dir(channel)
    print ''

    # test channel configuration
    print channel.config()
    print

    # Channel read method test
    val = channel.read()
    print 'channel()      = val = ' + str(channel())
    print 'channel.read() = val = ' + str(val)
    print 'len(val)       = ' + str(len(val))
    print 'type(val)      = ' + str(type(val))
    print 'iter(val)      = ' + str(iter(val))
    print ''

    # Channel factor test

    # Test factor set and get
    factor = random.random()
    channel.factor = factor
    if not channel.factor == factor:
        raise ValueError('Factor set/get failed')

    # Test factor divider
    factor = random.random()
    channel.factor = factor
    invals = [random.random() for i in range(3)]
    outvals = channel._factor_divide(invals)
    print 'factor = ' + str(channel.factor)
    print 'invals               = ' + str(invals)
    print '_factor_read(invals) = ' + str(outvals)
    for inval, outval in zip(invals, outvals):
        if not outval == inval / factor:
            raise ValueError('Factor read failed')

    # Test None and False factor
    channel.factor = None
    if channel.factor is not None:
        raise ValueError('Factor None test failed')

    channel.factor = False
    if channel.factor is not None:
        raise ValueError('Factor False test failed')

    print 'factor test    = True'


def writechannel_test():
    pass

if __name__ == '__main__':

    fooinstr = pym.instruments.FooInstrument()
    testch = fooinstr['random']
    testch.samples = 2
    readchannel_test(testch)
