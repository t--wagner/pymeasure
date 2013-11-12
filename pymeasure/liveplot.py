"""
    pymeasure.liveplotting
    ----------------------

    The liveplotting module is part of the pymeasure package. It allows
    parallel 1D and 2D live plotting of multiple incoming data streams. The
    focus of the module is on rapid and uncomplicated displaying of data
    streams. Liveplotting makes adding and removing streams as easy as
    possible. Although the direct focus is not so much on pretty figures, the
    access to the underlying matplotlib elements gives you almost unlimted
    power.

"""

from pymeasure.indexdict import IndexDict
import abc
import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

import warnings

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from mpl_toolkits.axes_grid1 import make_axes_locatable

from Queue import Queue


class LiveGraphBase(IndexDict):
    """Base class for differnt graphic backends.

    """

    def __init__(self, figure=None):
        """Initiate LivegraphBase class.

        Keyword arguments:
        figure -- Can take a matplotlib.figure.Figure otherwise it will be
                  created.

        """

        IndexDict.__init__(self)

        # Define matplotlib Figure
        if not figure:
            self._figure = Figure()
        else:
            self._figure = figure

        self._canvas = None

        # Set the number of colums
        self._columns = 1

        #self._clear_request = threading.event()
        self._snapshot_path_queue = Queue()

    def __setitem__(self, key, dataplot):
        """x.__setitem__(key, dataplot) <==> x['key'] = dataplot

        Add a Dataplot to Graph.
        """

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

    def add_subplot(self, *args, **kwargs):
        """Wrapper for matplotlib.figure.add_subplot(*args, **kwargs)

        """

        return self._figure.add_subplot(*args, **kwargs)

    def snapshot(self, filename):
        """Make a snapshot and save it as filename.

        """

        self._snapshot_path_queue.put(filename)

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
    """ LiveGraph backend for Tkinter.

    """

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
    __metaclass__ = abc.ABCMeta

    def __init__(self, axes):
        """Initiate DataplotBase class.

        """

        self._axes = axes
        self._exchange_queue = Queue()

    @property
    def axes(self):
        """The matplotlib.axes.Axes of Dataplot.

        """

        return self._axes

    @property
    def xlabel(self):
        return self._axes.get_xlabel()

    @xlabel.setter
    def xlabel(self, string):
        self._axes.set_xlabel(string)

    @property
    def ylabel(self):
        return self._axes.get_ylabel()

    @ylabel.setter
    def ylabel(self, string):
        self._axes.set_ylabel(string)

    @property
    def title(self):
        return self._axes.get_title()

    @title.setter
    def title(self, string):
        self._axes.set_title(string)

    def clear(self):
        """Clear the Dataplot immediately.

        """

        # Put a 'clear' meassage into the data exchange queue
        self._exchange_queue.put('clear')

    @abc.abstractmethod
    def add_data(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass


class Dataplot1d(DataplotBase):

    def __init__(self, axes, length, continuously, *line_args, **line_kwargs):
        """Initiate Dataplot1d class.

        """

        DataplotBase.__init__(self, axes)

        # Create emtpy line instance for axes
        self._line, = self._axes.plot([], [], *line_args, **line_kwargs)

        # Attributes for displayed number of points
        self._length = length
        self._continuously = continuously

        # Create list to contain plotting data
        self._xdata = list()
        self._ydata = list()

    @property
    def line(self, line):
        """matplotlib.lines.Line2D instance.

        """

        self._line = line

    @property
    def length(self):
        """Length of displayed datapoints.

        If continuously plotting is off Dataplot1d gets cleared when the number
        of added datapoints matches length. Otherwise this is the maximum
        number of displayed datapoints.

        """
        return self._length

    @length.setter
    def length(self, points):
        self._length = points

    @property
    def continuously(self):
        """Set continuously plotting True or False.

        If continuously plotting is True Dataplot1d gets cleared when the
        number of added datapoints matches length.

        """
        return self._continuously

    @continuously.setter
    def continuously(self, boolean):
        self._continuously = boolean

    def add_data(self, xdata, ydata):
        """Add a list of data to the plot.

        """

        # Put the incoming data into the data exchange queue
        self._exchange_queue.put([xdata, ydata])

    def update(self):
        """Update the dataplot with the incoming data.

        Process the added data, handle the maximum number of displayed
        datapoints and manage view limits.
        The update method is called by the Gaph build method and should not be
        called directly.

        """

        # Set up_to_date flag back to False.
        up_to_date = True

        # Keep going until the data exchange queue is empty.
        while not self._exchange_queue.empty():

            # Get a new package out of the exchange queue.
            package = self._exchange_queue.get()
            self._exchange_queue.task_done()

            # Try to add data to the x and y lists for plotting
            try:
                ydata = package.pop()
                xdata = package.pop()

                for xdatapoint in xdata:
                    self._xdata.append(xdatapoint)

                for ydatapoint in ydata:
                    self._ydata.append(ydatapoint)

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


class Dataplot2d(DataplotBase):

    def __init__(self, figure, axes, length, **image_kwargs):
        DataplotBase.__init__(self, axes)

        self._length = length

        self._exchange_queue = Queue()
        self._data = [[]]

        # Draw an empty image
        self._image = self._axes.imshow([[0]], aspect='auto', **image_kwargs)

        # Divide axes to fit colorbar (this works but don't aks me why)
        axes_divider = make_axes_locatable(self._axes)
        axes = axes_divider.append_axes("right",
                                        size="2.5%",
                                        pad=0.05)

        # Create colorbar and ignor warning caused because figure has only
        # one value.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._colorbar = figure.colorbar(self._image, axes)

        self._axes.set_axis_off()

    @property
    def image(self):
        return self._image

    @property
    def colorbar(self):
        """The matplotlib.colorbar.ColorBar of Dataplot2d.

        """

        return self._colorbar

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

            # Try to add data to plotting list
            try:
                for datapoint in package.pop():
                    self._data[-1].append(datapoint)

            # Look for a clearing request if the pop() attribute failed
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
                self._image.set_data([[0]])

            # Resacale the image
            self._image.autoscale()

        # Return the update flag. If True it will cause a redraw of the canvas.
        return up_to_date
