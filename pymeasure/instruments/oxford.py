# -*- coding: utf-8 -*-

from visa import VisaIOError

class OxfordInstrument(object):

    def __init__(self, instrument, delay=None, isobus=False):
        self.__dict__['_instr'] = instrument
        self.__dict__['delay'] = delay
        
        if isobus:
            self.__dict__['cmd_prefix'] = 2
        else:
            self.__dict__['cmd_prefix'] = 0

    def __getattr__(self, name):
        return getattr(self._instr, name)

    def __setattr__(self, name, value):
        setattr(self._instr, name, value)

    def write(self, command):

        command = command[self.cmd_prefix:]        
        
        while True:
            try:
                # The ips answers with the commands first letter if it
                # understood otherwise with '?'
                answer = self._instr.query(command, self.delay)
                if answer[0] == command[0]:
                    return answer[1:]
            except (VisaIOError, IndexError):
                # Once in a while IndexErrors occur if a previous command got
                # interrupted.
                self.flush()

    def flush(self):
        try:
            # Clear buffer
            while True:
                self._instr.read()
        except VisaIOError:
            #Buffer is clear when nothing is returned
            pass

