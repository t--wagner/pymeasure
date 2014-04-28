#import visa


class BackendBase(object):

    def __init__(self, driver):
        self._var = dict()
        self._ary = dict()
        self._driver = driver

    def get_var(self, *keys):
        var = []

        # Get var correspoding to key
        for key in keys:
            var.append(self._var[key])

        # Return var or list of vars
        if len(var) == 1:
            return var[0]
        else:
            return var

    def set_var(self, var_dcict):
        for key, value in var_dcict.items():
            self._var[key] = value

    def del_var(self, *keys):
        for key in keys:
            del self._var[key]

    def get_ary(self, key0, key1):
        return self._ary[key0][key1]

    def set_ary(self, key0, key1, value):
        try:
            self._ary[key0][key1] = value
        except KeyError:
            self._ary[key0] = {key1: value}

    def del_ary(self, key1, key2=None):
        if not key2:
            del self._ary[key1]
        else:
            del self._ary[key1][key2]


class PyVisaBackend(BackendBase):

    def __init__(self, visa_address, *args, **kwargs):
        driver = visa.instrument(visa_address, *args, **kwargs)
        BackendBase.__init__(self, driver)

    def read(self):
        return self._driver.read()

    def write(self, cmd):
        self._driver.write(cmd)

    def ask(self, cmd):
        return self._driver.ask(cmd)

    def ask_for_values(self, cmd):
        return self._driver.ask_for_values(cmd)