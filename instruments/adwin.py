# -*- coding: utf-8 -*-

from pymeasure.case import Instrument
import ADwin


class AdwinBool:

    def __init__(self, index, writeable=True):
        self.index = index
        self.writeable = writeable

    def __get__(self, instance, *args, **kwargs):
        return bool(instance._instr.Get_Par(self.index))

    def __set__(self, instance, value, *args, **kwargs):
        if self.writeable:
            return instance._instr.Set_Par(int(self.index), value)
        else:
            raise AttributeError("can't set attribute")


class AdwinInt:

    def __init__(self, index, writeable=True):
        self.index = index
        self.writeable = writeable

    def __get__(self, instance, *args, **kwargs):
        return instance._instr.Get_Par(self.index)

    def __set__(self, instance, value, *args, **kwargs):
        if self.writeable:
            return instance._instr.Set_Par(self.index, value)
        else:
            raise AttributeError("can't set attribute")


class AdwinFloat:

    def __init__(self, index, writeable=True):
        self.index = index
        self.writeable = writeable

    def __get__(self, instance, *args, **kwargs):
        return instance._instr.Get_FPar(self.index)

    def __set__(self, instance, value, *args, **kwargs):
        if self.writeable:
            return instance._instr.Set_FPar(self.index, value)
        else:
            raise AttributeError("can't set attribute")


class AdwinData:
    pass


class AdwinFData:
    pass


class AdwinFifo:
    pass


class AdwinFFifo:
    pass


class AdwinInstrument(Instrument):

    def __init__(self, device_number=1, processor_type=12, reset=False, name=''):
        super().__init__(name, instr=ADwin.ADwin(device_number))

        if reset:
            self.reset(processor_type, reset)

    def reset(self, processor_type, boolean=False):
        """Reboot the ADwin operation system.

        """
        if boolean is True:
            os_file = '{}adwin{}.btl'.format(self._instr.ADwindir, processor_type)
            self._instr.Boot(os_file)

    def test_version(self):
        """Checks if the correct operating system for the processor has been
        loaded and if the processor can be accessed.

        """
        if self._instr.Test_Version() == 0:
            return True
        else:
            return False

    @property
    def free_memory(self):
        """Determines the free memory for the different memory types.

        """
        free_memory = {}
        free_memory['pm'] = self._instr.Free_Mem(1)
        free_memory['em'] = self._instr.Free_Mem(2)
        free_memory['dm'] = self._instr.Free_Mem(3)
        free_memory['dx'] = self._instr.Free_Mem(4)
        free_memory['cm'] = self._instr.Free_Mem(5)
        free_memory['um'] = self._instr.Free_Mem(6)

        return free_memory

    @property
    def device_number(self):
        """ADwin device number.

        """
        return self._instr.DeviceNo

    @property
    def processor(self):
        """Processor type of the system.

        """
        processor_nr = self._instr.Processor_Type()

        if processor_nr == 2:
            processor_str = 'T2'
        elif processor_nr == 4:
            processor_str = 'T4'
        elif processor_nr == 5:
            processor_str = 'T5'
        elif processor_nr == 8:
            processor_str = 'T8'
        elif processor_nr == 9:
            processor_str = 'T9'
        elif processor_nr == 1010:
            processor_str = 'T10'
        elif processor_nr == 1011:
            processor_str = 'T11'
        elif processor_nr == 1012:
            processor_str = 'T12'
        elif processor_nr == 0:
            processor_str = 'Error'

        return processor_str

    @property
    def workload(self):
        """Processor workload in percentage.

        """
        return self._instr.Workload()

    @property
    def version(self):
        return self._instr.version

    @property
    def error(self):
        nr_error = self._instr.Get_Last_Error()
        return self._instr.Get_Last_Error_Text(nr_error)