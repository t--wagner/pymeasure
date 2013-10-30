from .case import _IndexDict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
import Tkinter
import Queue


class Graph(_IndexDict):

    def __init__(self):
        _IndexDict.__init__(self)

        #Create matplotlib Figure
        self._figure = Figure()

        #Setup the TKInter window with the canvas and a toolbar
        self._root = Tkinter.Tk()
        self._canvas = FigureCanvasTkAgg(self._figure, master=self._root)
        self._tkwidget = self._canvas.get_tk_widget()
        self._toolbar = NavigationToolbar2TkAgg(self._canvas, self._root)
        self._toolbar.update()
        self._tkwidget.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
        self._canvas.show()

        #self._clear_request = threading.event()
        self._save_path = Queue.Queue()

    def __setitem__(self, key, dataplot):
        if isinstance(dataplot, Dataplot):
            _IndexDict.__setitem__(self, key, dataplot)
        else:
            raise TypeError('item must be a Dataplot.')

    @property
    def dataplots(self):
        return [index_key for index_key in enumerate(self._odict.keys())]

    @property
    def figure(self):
        return self._figure

    @property
    def colums(self):
        return self._colums

    @colums.setter
    def colums(self, nr):
        self._colums = nr

    @property
    def rows(self):
        rows = self.__len__() / self._colums
        if self.__len__() % self._colums == 0:
            return rows
        else:
            return rows + 1

    def save(self, path):
        self._save_path.put(path)

    def create(self):
        nr = 1
        for key, dataplot in self.__iter__():
            dataplot.axes = self.figure.add_subplot(self.rows,
                                                    self._colums, nr)
            nr += 1
        self.run()

    def update(self):
        update = False

        #Get new data and update the Plots
        for key, subplot in self.__iter__():
            if subplot.update():
                update = True

        #Redraw the canvas
        if update:
            self._canvas.draw()

    def run(self):
        self.update()

        while not self._save_path.empty():
            path = self._save_path.get()
            self._figure.savefig(path)
            self._save_path.task_done()

        self._root.after(25, self.run)


class Dataplot(object):

    def __init__(self):
        self._axes = None

    @property
    def axes(self):
        self._axes

    @axes.setter
    def axes(self, axes):
        self._axes = axes


class DataplotFan(Dataplot):

    def __init__(self, *dataplots1d):
        Dataplot.__init__(self)

        self._axes = None
        self._dataplots1d = dataplots1d

    @property
    def axes(self):
        self._axes

    @axes.setter
    def axes(self, axes):
        for dataplot1d in self._dataplots1d:
            dataplot1d.axes = axes

    def update(self):

        need_update = False

        for dataplot1d in self._dataplots1d:
            if dataplot1d.update():
                need_update = True

        return need_update


class Dataplot1d(Dataplot):

    def __init__(self, length):
        Dataplot.__init__(self)

        self._line = None
        self._length = length
        self._xqueue = Queue.Queue()
        self._xdata = list()
        self._yqueue = Queue.Queue()
        self._ydata = list()

    @property
    def line(self, line):
        self._line = line

    def add_xdata(self, xdata):
        try:
            for xdatapoint in xdata:
                self._xqueue.put(xdatapoint)
        except TypeError:
            self._xqueue.put(xdata)

    def add_ydata(self, ydata):
        try:
            for ydatapoint in ydata:
                self._yqueue.put(ydatapoint)
        except TypeError:
            self._yqueue.put(ydata)

    def add_data(self, xdata, ydata):
        self.add_xdata(xdata)
        self.add_ydata(ydata)

    def update(self):

        #Set update flag back to False
        need_update = False

        # Check the queues for new data
        while not self._xqueue.empty():
            #Clear data if trace is at the end
            if len(self._xdata) == self._length:
                del self._xdata[:]
                del self._ydata[:]

            #Get a new datapoint
            self._xdata.append(self._xqueue.get())
            self._xqueue.task_done()
            self._ydata.append(self._yqueue.get())
            self._yqueue.task_done()

            #Set the update flag to True
            need_update = True

        # Update the plot with the new data if necassary
        if need_update:
            try:
                self._line.set_data(self._xdata,
                                    self._ydata[0:len(self._xdata)])
                self._axes.relim()
                self._axes.autoscale_view()
            except AttributeError:
                self._line, = self._axes.plot(self._xdata,
                                              self._ydata[0:len(self._xdata)])

        # Return the update flag. If True it will cause a redraw of the canvas.
        return need_update


class Dataplot2d(Dataplot):

    def __init__(self, length):
        Dataplot.__init__(self)

        self._image = None
        self._colorbar = None
        self._length = length

        self._queue = Queue.Queue()
        self._data = [[]]

    @property
    def image(self):
        return self._image

    def add_data(self, data):
        for datapoint in data:
            self._queue.put(datapoint)

    def colorbar(self):
        return self._colorbar

    def update(self):

        need_update = False

        # Check the queues for new data
        while not self._queue.empty():

            self._data[-1].append(self._queue.get())
            self._queue.task_done()

            #Clear data if trace is at the end
            if len(self._data[-1]) == self._length:

                try:
                    self._image.set_array(self._data)
                    self._image.autoscale()
                except AttributeError:
                    #self._image = self._axes.matshow(self._data,aspect='auto')
                    self._image = self._axes.imshow(self._data, aspect='auto')
                    self._axes.set_axis_off()
                    #self._colorbar = colorbar(self._image, ax=self._axes)

                self._data.append([])
                need_update = True

        return need_update
