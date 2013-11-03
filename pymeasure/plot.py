from pymeasure.case import IndexDict
import Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from Queue import Queue
from future_builtins import zip
from collections import deque


class Graph(IndexDict):

    def __init__(self, figure=Figure()):
        IndexDict.__init__(self)

        #Create matplotlib Figure
        if figure:
            self._figure = figure
        else:
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
            IndexDict.__setitem__(self, key, dataplot)
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
        for dataplot in self.__iter__():
            dataplot.axes = self.figure.add_subplot(self.rows,
                                                    self._colums, number)
            number += 1
        self.run()

    def run(self):

        up_to_date = True

        # Call all subplots to check for updates
        for subplot in self.__iter__():
            if not subplot.update():
                up_to_date = False

        #Redraw the canvas if not up to date
        if not up_to_date:
            self._canvas.draw()

        while not self._save_path.empty():
            path = self._save_path.get()
            self._figure.savefig(path)
            self._save_path.task_done()

        self._root.after(25, self.run)


class Dataplot(object):

    def __init__(self, axes=None):
        self._axes = axes

    @property
    def axes(self):
        return self._axes

    @axes.setter
    def axes(self, axes):
        self._axes = axes


class MultiDataplot1d(IndexDict, Dataplot):

    def __init__(self):
        IndexDict.__init__(self)
        Dataplot.__init__(self)

        self._axes = None

    @property
    def axes(self):
        return self._axes

    @axes.setter
    def axes(self, axes):
        for dataplot1d in self.__iter__():
            dataplot1d.axes = axes

    def update(self):

        up_to_date = True

        for dataplot1d in self.__iter__():
            if not dataplot1d.update():
                up_to_date = False

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

        # Set up_to_date flag back to False.
        up_to_date = True

        # Keep going until the exchange queue is empty.
        while not self._data_queue.empty():

            # Get a xy_dataset out of the exchange queue.
            xy_dataset = self._data_queue.get()
            self._data_queue.task_done()

            # Handel the maximum number of displayed points.
            if len(self._xdata) == self._points:
                #Remove oldest datapoint if plotting continuously.
                if self._continuously:
                    self._xdata.popleft()
                    self._ydata.popleft()
                # Clear all displayed datapoints otherwise.
                else:
                    self._xdata.clear()
                    self._ydata.clear()

            # Add xy_dataset for plotting
            self._xdata.append(xy_dataset[0])
            self._ydata.append(xy_dataset[1])

            #Set the up_to_date flag to True for redrawing
            up_to_date = False

        # Update the plot with the new data if necassary
        if not up_to_date:
            try:
                # Update displayed data.
                self._line.set_data(self._xdata, self._ydata)
                # Recompute the data limits.
                self._axes.relim()
                # Autoscale the view limits using the data limit.
                self._axes.autoscale_view()
            except AttributeError:
                # Create matplotlib.lines.Line2D
                self._line, = self._axes.plot(self._xdata, self._ydata)

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

        up_to_date = True

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
                up_to_date = False

        return up_to_date
