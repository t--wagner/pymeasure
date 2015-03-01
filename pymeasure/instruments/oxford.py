# -*- coding: utf-8 -*-

import time
from visa import VisaIOError


def write(instrument, command):
    while True:
        try:
            # The ips answers with the commands first letter if it
            # understood otherwise with '?'
            answer = instrument.query(command, 0.1)
            if answer[0] == command[0]:
                return answer[1:]
        except (VisaIOError, IndexError):
            # Once in a while IndexErrors occur if a previous command got
            # interrupted.
            flush_buffer(instrument)

def flush_buffer(instrument):
    try:
        # Clear buffer
        while True:
            instrument.read()
            time.sleep(0.1)
    except VisaIOError:
        #Buffer is clear when nothing is returned
        pass

