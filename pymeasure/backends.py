import visa


class PyVisaBackend(object):

    def __init__(self, visa_address, *args, **kwargs):
        self._attr = dict()
        self._visa = visa.instrument(visa_address, *args, **kwargs)

    def get_attr(self, key0, key1):
        return self._attr[key0][key1]

    def set_attr(self, key0, key1, value):
        self._attr[key0][key1] = value

    def del_attr(self, key0, key1):
        del self._attr[key0][key1]

    def read(self):
        return self._visa.read()

    def write(self, cmd):
        self._visa.write(cmd)

    def ask(self, cmd):
        return self._visa.ask(cmd)

    def ask_for_values(self, cmd):
        return self._visa.ask_for_values(cmd)
