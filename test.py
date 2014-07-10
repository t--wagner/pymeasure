# -*- coding: utf-8 -*


class TestBase(object):

    def __init__(self):
        self._factor = 1

    @property
    def factor(self):
        return self._factor

    def read(self):
        pass

    def write(*values):
        pass

class Test(TestBase):

    def __dir__(self):
        return []

if __name__ == '__main__':
    tb = TestBase()
    print dir(tb)

    t = Test()
    print dir(t)