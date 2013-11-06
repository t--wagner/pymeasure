"""
The liveplotting module is part of the pymeasure package. It allows parallel
1D and 2D live plotting of multiple incoming datastreams with python. The focus
of the module is on rapid and uncomplicated displaying of the data streams.
Liveplotting makes adding and removing streams as easy as possible. Although
the direct focus is not so much on pretty graphs the access to the underlying
matplotlib elements gives you almost unlimted power.

"""

from pymeasure.indexdict import IndexDict

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from mpl_toolkits.axes_grid1 import make_axes_locatable

from Queue import Queue
#from collections import deque


class LiveGraphBase(IndexDict):
    """Base class for differnt backends
    """

    def __init__(self, figure=None):
        IndexDict.__init__(self)

        # Define matplotlib Figure
        if not figure:
            self._figure = Figure()
        else:
            self._figure = figure

        self._canvas = None

        # Set the number of colums
        self._colums = 1

        #self._clear_request = threading.event()
        self._snapshot_path_queue = Queue()

    def __setitem__(self, key, dataplot):
        if isinstance(dataplot, DataplotBase):
            IndexDict.__setitem__(self, key, dataplot)
        else:
            raise TypeError('item must be a Dataplot.')

    @property
    def figure(self):
        """The matplotlib.figure.Figure of Graph.

        """
        return self._figure

    def dataplots(self):
        """Return a list of (index, key) pairs in Graph.

        """

        return [index_key for index_key in enumerate(self._odict.keys())]

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

    def snapshot(self, filename):
        """Make a snapshot and save it as filename.

        """

        self._snapshot_path_queue.put(filename)

    def build(self):
        """Create the matplotlib.axes.Axes for the Dataplot items.

        Create the matplotlib.axes.Axe and pass them together with the
        matplotlib figure to the build methods of the added Dataplot items.
        This build method must be called after adding all dataplots to the
        graph and before run.

        """

        #Iterate through all dataplots
        for index, dataplot in enumerate(self.__iter__(), 1):

            #build axes for dataplot
            axes = self.figure.add_subplot(self.rows, self._colums, index)

            # Call build method of dataplot
            dataplot.build(axes, self._figure)

    def update(self):
        """Update all dataplots and redraw the canvas if necassary.

        Calls the update methods of all dataplots and makes requested
        snapshots.
        The update method is called periodically by the run method of the
        backend and should not be used directly.

        """

        # Set up_to_date flag back to True
        up_to_date = True

        # Iterate through all subplots and check for updates
        for subplot in self.__iter__():
            if not subplot.update():
                up_to_date = False

        # Save a snapshot if requested
        while not self._snapshot_path_queue.empty():
            path = self._snapshot_path_queue.get()
            self._snapshot_path_queue.task_done()
            self._figure.savefig(path)

        # Redraw the canvas
        if not up_to_date:
            self._canvas.draw()


class LiveGraphTk(LiveGraphBase):

    def __init__(self, figure=None, master=None):
        LiveGraphBase.__init__(self, figure=figure)

        #Setup the TKInter window with the canvas and a toolbar
        if not master:
            self._master = Tk.Tk()
        else:
            self._master = master

        # build canvas for Tk
        self._canvas = FigureCanvasTkAgg(self._figure, master=self._master)
        self._canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # Navigation Toolbar
        self._toolbar = NavigationToolbar2TkAgg(self._canvas, self._master)
        self._toolbar.update()
        self._canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def run(self, delay=25):
        """Calls the update method periodically with the delay in milliseconds.

        Decrease the delay to make the plotting smoother and increase it to
        reduce the preformance. For live plotting the delay must fit the rate
        of the incoming data.

        Keyword arguments:
        delay -- the delay in millisconds after each call (default 25)

        """

        # Call the update function
        self.update()

        # Call run again afer the delay time
        self._master.after(delay, self.run, delay)


class DataplotBase(object):

    def __init__(self):
        self._figure = None
        self._axes = None

        self._exchange_queue = Queue()

    @property
    def figure(self):
        return self._figure

    @figure.setter
    def figure(self, figure):
        self._figure = figure

    @property
    def axes(self):
        return self._axes

    @axes.setter
    def axes(self, axes):
        self._axes = axes

    def build(self, axes, figure):

        # Set axes and figure attributes
        self._axes = axes
        self._figure = figure

    def clear(self):

        # Put a 'clear' meassage into the data exchange queue
        self._exchange_queue.put('clear')


class Dataplot1d(DataplotBase):

    def __init__(self, length=float('+inf'), continuously=False):
        DataplotBase.__init__(self)

        self._line = None
        self._length = length
        self._continuously = continuously

        self._xdata = list()
        self._ydata = list()

    @property
    def line(self, line):
        self._line = line

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, points):
        self._length = points

    @property
    def continuously(self):
        return self._continuously

    @continuously.setter
    def continuously(self, boolean):
        self._continuously = boolean

    def build(self, axes, figure):

        # Call build method of the base class
        DataplotBase.build(self, axes, figure)

        # Build matplotlib.lines.Line2D
        self._line, = self._axes.plot(self._xdata, self._ydata)

    def add_data(self, xdata, ydata):

        # Put the incoming data into the data exchange queue
        self._exchange_queue.put([xdata, ydata])

    def update(self):

        # Set up_to_date flag back to False.
        up_to_date = True

        # Keep going until the data exchange queue is empty.
        while not self._exchange_queue.empty():

            # Get a new package out of the exchange queue.
            package = self._exchange_queue.get()
            self._exchange_queue.task_done()

            # Try to add data to the x and y lists for plotting
            try:
                self._ydata += package.pop()
                self._xdata += package.pop()

            # Look for a clearing request if the pop() attribute failed
            except AttributeError:
                meassage = package
                if meassage == 'clear':
                    del self._xdata[:]
                    del self._ydata[:]

            # Handle the maximum number of displayed points.
            while len(self._xdata) > self._length:

                #Remove oldest datapoints if plotting continuously.
                if self._continuously:
                    del self._xdata[:-self._length]
                    del self._ydata[:-self._length]

                # Clear all displayed datapoints otherwise.
                else:
                    del self._xdata[:self._length]
                    del self._ydata[:self._length]

            #Set the up_to_date flag to True for redrawing
            up_to_date = False

        # Update the line with the new data if available
        if not up_to_date:

            # Update displayed data.
            self._line.set_data(self._xdata, self._ydata)

            # Recompute the data limits.
            self._axes.relim()

            # Resacale the view limits using the previous computed data limit.
            self._axes.autoscale_view()

        # Return the update flag. If True it will cause a redraw of the canvas.
        return up_to_date


class MultiDataplot1d(IndexDict, DataplotBase):

    def __init__(self):
        IndexDict.__init__(self)
        DataplotBase.__init__(self)

    @property
    def axes(self):
        return self._axes

    @axes.setter
    def axes(self, axes):
        for dataplot1d in self.__iter__():
            dataplot1d.axes = axes

    def build(self, axes, figure):
        for dataplot1d in self.__iter__():
            dataplot1d.build(axes, figure)

    def update(self):

        up_to_date = True

        for dataplot1d in self.__iter__():
            if not dataplot1d.update():
                up_to_date = False

        return up_to_date


class Dataplot2d(DataplotBase):

    def __init__(self, length=float('+inf')):
        DataplotBase.__init__(self)

        self._image = None
        self._colorbar = None
        self._length = length

        self._exchange_queue = Queue()
        self._data = [[]]

    @property
    def image(self):
        return self._image

    @property
    def colorbar(self):
        return self._colorbar

    def build(self, axes, figure):

        # Call the build function of the DataplotBase class
        DataplotBase.build(self, axes, figure)

        # Draw an empty image
        self._image = self._axes.imshow([[0]],
                                        aspect='auto',
                                        interpolation='none')

        # Make a colorbar (this works, don't aks me why)
        axes_divider = make_axes_locatable(self._axes)
        axes = axes_divider.append_axes("right",
                                        size="2.5%",
                                        pad=0.05)
        self._figure.colorbar(self._image, axes)

        self._axes.set_axis_off()

    def add_data(self, data):

        # Put the incoming data into the data exchange queue
        self._exchange_queue.put([data])

    def next_line(self):

        # Put a 'next' meassage into the data exchange queue
        self._exchange_queue.put('next')

    def update(self):

        #Set up_to_date flag back to True
        up_to_date = True

        # Check the queues for new data
        while not self._exchange_queue.empty():

            # Get new package out of the exchange queue.
            package = self._exchange_queue.get()
            self._exchange_queue.task_done()

            try:
                self._data[-1] += package.pop()
            except:
                message = package
                if message == 'clear':
                    self._data = [[]]
                    up_to_date = False
                elif message == 'next':
                    self._data.append([])

            # Handle the maximum number of displayed points.
            while len(self._data[-1]) > self._length:

                split = self._data[-1][self._length:]
                del self._data[-1][self._length:]
                self._data.append(split)

                #Set the up_to_date flag to True for redrawing
                up_to_date = False

        # Update the image with the new data if available
        if not up_to_date:

            # Try to set the new data
            try:
                self._image.set_data(self._data[:-1])
            # If no data available plot an empty image
            except TypeError:
                self._image.set_data([[float('nan')]])

            # Resacale the image
            self._image.autoscale()

        # Return the update flag. If True it will cause a redraw of the canvas.
        return up_to_date
