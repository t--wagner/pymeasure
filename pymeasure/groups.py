# -*- coding: utf-8 -*-

def counter(iterable, steps):
    """Sends after number of steps a True status.

    """

    iterator = iter(iterable)

    while True:
        for value in xrange(steps):
            status = False
            if value == steps - 1:
                status = True

            yield (next(iterator), status)
