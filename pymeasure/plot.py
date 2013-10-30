from .case import _IndexDict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
import Tkinter
from Queue import Queue
from future_builtins import zip
from collections import deque


class Graph(_IndexDict):

    def __init__(self):
        _IndexDict.__init__(self)

        #Create matplotlib Figure
        self._figure = Figure()
        self._colums = 1

        #Setup the TKInter window with the canvas and a toolbar
        self._root = Tkinter.Tk()
        self._canvas = FigureCanvasTkAgg(self._figure, master=self._root)
        self._tkwidget = self._canvas.get_tk_widget()
        self._toolbar = NavigationToolbar2TkAgg(self._canvas, self._root)
        self._toolbar.update()
        self._tkwidget.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
        self._canvas.show()

        #self._clear_request = threading.event()
        self._save_path = Queue()

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
    def colums(self, number):
        self._colums = number

    @property
    def rows(self):
        rows = self.__len__() / self.colums
        if self.__len__() % self.colums == 0:
            return rows
        else:
            return rows + 1

    def save(self, path):
        self._save_path.put(path)

    def create(self):
        number = 1
        for key, dataplot in self.__iter__():
            dataplot.axes = self.figure.add_subplot(self.rows,
                                                    self._colums, number)
            number += 1
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
        return self._axes

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
        return self._axes

    @axes.setter
    def axes(self, axes):
        for dataplot1d in self._dataplots1d:
            dataplot1d.axes = axes

    def update(self):

        up_to_date = False

        for dataplot1d in self._dataplots1d:
            if dataplot1d.update():
                up_to_date = True

        return up_to_date


class Dataplot1d(Dataplot):

    def __init__(self, points=None, continuously=False):
        Dataplot.__init__(self)

        self._line = None
        self._points = points
        self._continuously = continuously
        self._data_queue = Queue()
        self._xdata = deque()
        self._ydata = deque()

    @property
    def line(self, line):
        self._line = line

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def continuously(self):
        return self._continuously

    @continuously.setter
    def continuously(self, boolean):
        self._continuously = boolean

    def add_data(self, xdata, ydata):
        if not len(xdata) == len(ydata):
            raise ValueError('x and y must have same length')

        for xy_dataset in zip(xdata, ydata):
            self._data_queue.put(xy_dataset)

    def update(self):

        #Set update flag back to False
        up_to_date = False

        while not self._data_queue.empty():
            if len(self._xdata) == self._points:
                if self._continuously:
                    self._xdata.popleft()
                    self._ydata.popleft()
                else:
                    self._xdata.clear()
                    self._ydata.clear()

            #Get xy_dataset out of the data_queue
            xy_dataset = self._data_queue.get()
            self._data_queue.task_done()
            self._xdata.append(xy_dataset[0])
            self._ydata.append(xy_dataset[1])

            #Set the update flag to True
            up_to_date = True

        # Update the plot with the new data if necassary
        if up_to_date:
            try:
                self._line.set_data(self._xdata,
                                    self._ydata)
                self._axes.relim()
                self._axes.autoscale_view()
            except AttributeError:
                self._line, = self._axes.plot(self._xdata,
                                              self._ydata)

        # Return the update flag. If True it will cause a redraw of the canvas.
        return up_to_date


class Dataplot2d(Dataplot):

    def __init__(self, points):
        Dataplot.__init__(self)

        self._image = None
        self._colorbar = None
        self._points = points

        self._data_queue = Queue()
        self._data = [[]]

    @property
    def image(self):
        return self._image

    @property
    def colorbar(self):
        return self._colorbar

    def add_data(self, data):
        for datapoint in data:
            self._data_queue.put(datapoint)

    def update(self):

        up_to_date = False

        # Check the queues for new data
        while not self._data_queue.empty():

            self._data[-1].append(self._data_queue.get())
            self._data_queue.task_done()

            #Clear data if trace is at the end
            if len(self._data[-1]) == self._points:

                try:
                    self._image.set_array(self._data)
                    self._image.autoscale()
                except AttributeError:
                    #self._image = self._axes.matshow(self._data,aspect='auto')
                    self._image = self._axes.imshow(self._data, aspect='auto')
                    self._axes.set_axis_off()
                    #self._colorbar = colorbar(self._image, ax=self._axes)

                self._data.append([])
                up_to_date = True

        return up_to_date
