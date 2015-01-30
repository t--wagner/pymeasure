# -*- coding: utf-8 -*-

import random
import math
from pymeasure.case import *
from pymeasure import pym


def readchannel_test(channel):

    print 'Channel test:'
    print '-------------'
    print channel
    print ''

    print 'Channel dir:'
    print '----------------'
    print dir(channel)
    print ''

    # test channel configuration
    print 'Channel configuration:'
    print '----------------------'
    print repr(channel.config())
    print

    # Channel factor test
    print 'Channel factor:'
    print '---------------'

    # Test factor set and get
    factor = random.random()
    channel.factor = factor
    if not channel.factor == factor:
        raise ValueError('Factor set/get failed')

    # Test factor divider
    factor = random.random()
    channel.factor = factor
    invals = [random.random() for i in range(3)]
    dvals = channel._factor_divide(invals)
    mvals = channel._factor_multiply(invals)
    print 'factor                   = ' + str(channel.factor)
    print 'invals                   = ' + str(invals)
    print '_factor_divide(invals)   = ' + str(dvals)
    print '_factor_multiply(invals) = ' + str(mvals)
    for inval, dval in zip(invals, dvals):
        if not dval == inval / factor:
            raise ValueError('Factor divide failed')

    for inval, mval in zip(invals, mvals):
        if not mval == inval * factor:
            raise ValueError('Factor multiply failed')

    # Test None and False factor
    channel.factor = None
    if channel.factor is not None:
        raise ValueError('Factor None test failed')

    channel.factor = False
    if channel.factor is not None:
        raise ValueError('Factor False test failed')

    print 'factor test              = True'
    print ''

    # Channel read method test
    print 'Channel read():'
    print '---------------'
    val = channel.read()
    print 'channel()      = val = ' + str(channel())
    print 'channel.read() = val = ' + str(val)
    print 'len(val)       = ' + str(len(val))
    print 'type(val)      = ' + str(type(val))
    print 'iter(val)      = ' + str(iter(val))
    print ''


def writechannel_test(channel):
    readchannel_test(channel)

    print 'Channel write():'
    print '---------------'
    vals = [random.random() for i in range(1)]
    print 'channel()       = ' + str(channel(*vals))
    print 'channel.write() = ' + str(channel.write(*vals))
    print


def instrument_test(instrument):

    for channel in instrument:
        if isinstance(channel, ChannelWrite):
            writechannel_test(channel)
        elif isinstance(channel, ChannelRead):
            readchannel_test(channel)


def ramp(start, stop, stepsize):
    stepsize = stepsize
    points = int((stop - start) / stepsize)

    # Return generator for negative or positive stepping
    if math.copysign(1, points) > 0:
        steps = (start + n * stepsize for n in xrange(1, points + 1, 1))
    else:
        steps = (start + n * stepsize for n in xrange(-1, points - 1, -1))

    return list(steps) + [stop]

if __name__ == '__main__':

    fooinstr = pym.instruments.FooInstrument()
    instrument_test(fooinstr)

    out = fooinstr[1]
    out.steptime = 0.1
    out.steprate = 0.1
