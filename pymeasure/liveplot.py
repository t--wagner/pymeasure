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

import sys
from pymeasure.indexdict import IndexDict
import abc
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

import warnings
import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.colors import Normalize, LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from Queue import Queue
from threading import Event


class LiveGraphBase(IndexDict):
    """Base class for differnt graphic backends.

    """

    def __init__(self, figure=None):
        """Initiate LivegraphBase class.

        Keyword arguments:
        figure -- Can take an instance of matplotlib.figure.Figure otherwise it
                  will be created.

        """

        IndexDict.__init__(self)

        # Define matplotlib Figure
        if not figure:
            self._figure = mpl.figure.Figure()
        else:
            self._figure = figure

        # Set the number of colums
        self._columns = 1

        #self._clear_request = threading.event()
        self._snapshot_path_queue = Queue()
        self._tasks = Queue()

    def __setitem__(self, key, dataplot):
        """x.__setitem__(key, dataplot) <==> x['key'] = dataplot

        Add a Dataplot to Graph.
        """

        if isinstance(dataplot, DataplotBase):
            IndexDict.__setitem__(self, key, dataplot)
        else:
            raise TypeError('item must be a Dataplot.')

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

        while not self._snapshot_path_queue.empty():
            pass

    def _add_task(self, function, *args, **kargs):
        """Add a task function(*args, **kwargs) to the task queue.

        """
        self._tasks.put((function, args, kargs))

    def _update(self):
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
            subplot._update()
            if subplot._request_update.is_set():
                up_to_date = False
                subplot._request_update.clear()

        # Process all tasks
        while not self._tasks.empty():
            func, args, kargs = self._tasks.get()
            func(*args, **kargs)
            self._tasks.task_done()

        # Save a snapshot if requested
        while not self._snapshot_path_queue.empty():
            path = self._snapshot_path_queue.get()
            self._snapshot_path_queue.task_done()
            self._figure.savefig(path)

        # Redraw the canvas
        if not up_to_date:
            self._figure.tight_layout()
            self._figure.canvas.draw()


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
        canvas = FigureCanvasTkAgg(self._figure, master=self._master)
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # Navigation Toolbar
        self._toolbar = NavigationToolbar2TkAgg(canvas, self._master)
        self._toolbar.update()
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def run(self, delay=25):
        """Calls the update method periodically with the delay in milliseconds.

        Decrease the delay to make the plotting smoother and increase it to
        reduce the preformance. For live plotting the delay must fit the rate
        of the incoming data.

        Keyword arguments:
        delay -- the delay in millisconds after each call (default 25)

        """

        # Call the update function
        self._update()

        # Call run again afer the delay time
        self._master.after(delay, self.run, delay)


class DataplotBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph, axes):
        """Initiate DataplotBase class.

        """

        self._graph = graph
        self._axes = axes
        self._exchange_queue = Queue()
        self._request_update = Event()

    def clear(self):
        """Clear the Dataplot immediately.

        """

        # Put a 'clear' meassage into the data exchange queue
        self._exchange_queue.put('clear')

    @abc.abstractmethod
    def add_data(self):
        pass

    @abc.abstractmethod
    def _update(self):
        pass


class LabelConf1d(object):

    def __init__(self, graph, axes):
        self._graph = graph
        self._axes = axes

    @property
    def title(self):
        return self._axes.get_title()

    @title.setter
    def title(self, string):
        self._graph._add_task(self._axes.set_title, string)

    @property
    def xaxis(self):
        return self._axes.get_xlabel()

    @xaxis.setter
    def xaxis(self, string):
        self._graph._add_task(self._axes.set_xlabel, string)

    @property
    def yaxis(self):
        return self._axes.get_ylabel()

    @yaxis.setter
    def yaxis(self, string):
        self._graph._add_task(self._axes.set_ylabel, string)


class LineConf(object):

    def __init__(self, graph, line):
        self._graph = graph
        self._line = line

    @property
    def style(self):
        return self._line.get_linestyle()

    @style.setter
    def style(self, linestyle):

        # Handle wrong input to avoid crashing running liveplot
        if not linestyle in self._line.lineStyles.keys():
            raise ValueError('not a valid linestyle')

        self._graph._add_task(self._line.set_linestyle, linestyle)

    @property
    def draw(self):
        return self._line.get_drawstyle()

    @draw.setter
    def draw(self, drawstyle):

        # Handle wrong input to avoid crashing running liveplot
        if not drawstyle in self._line.drawStyleKeys:
            raise ValueError('not a valid drawstyle')

        self._graph._add_task(self._line.set_drawstyle, drawstyle)

    @property
    def color(self):
        return self._line.get_color()

    @color.setter
    def color(self, color):

        # Handle wrong input to avoid crashing running liveplot
        if not mpl.colors.is_color_like(color):
            raise ValueError('not a valid color')

        self._graph._add_task(self._line.set_color, color)

    @property
    def width(self):
        return self._line.get_linewidth()

    @width.setter
    def width(self, linewidth):

        # Handle wrong input to avoid crashing running liveplot
        linewidth = float(linewidth)
        self._graph._add_task(self._line.set_linewidth, linewidth)


class MarkerConf(object):

    def __init__(self, graph, line):
        self._graph = graph
        self._line = line

    @property
    def style(self):
        marker = self._line.get_marker()

        if marker == 'None':
            marker = None

        return marker

    @style.setter
    def style(self, marker):

        # Handle wrong input to avoid crashing running liveplot
        if marker in [None, False]:
            marker = 'None'
        elif not marker in self._line.markers.keys():
            raise ValueError('not a valid marker')

        self._graph._add_task(self._line.set_marker, marker)

    @property
    def facecolor(self):
        return self._line.get_markerfacecolor()

    @facecolor.setter
    def facecolor(self, color):

        # Handle wrong input to avoid crashing running liveplot
        if not mpl.colors.is_color_like(color):
            raise ValueError('not a valid color')

        self._graph._add_task(self._line.set_markerfacecolor, color)

    @property
    def edgecolor(self):
        return self._line.get_markeredgecolor()

    @edgecolor.setter
    def edgecolor(self, color):

        # Handle wrong input to avoid crashing running liveplot
        if not mpl.colors.is_color_like(color):
            raise ValueError('not a valid color')

        self._graph._add_task(self._line.set_markeredgecolor, color)

    @property
    def size(self):
        return self._line.get_markersize()

    @size.setter
    def size(self, markersize):

        # Handle wrong input to avoid crashing running liveplot
        markersize = float(markersize)

        self._graph._add_task(self._line.set_markersize, markersize)


class XaxisConf(object):

    def __init__(self, axes, request_update):
        self._axes = axes
        self._request_update = request_update

        self._scale = 'linear'

    @property
    def autoscale(self):
        return self._axes.get_autoscalex_on()

    @autoscale.setter
    def autoscale(self, boolean):

        # Check for bool type
        if not isinstance(boolean, bool):
            raise TypeError('not bool')

        self._axes.set_autoscalex_on(boolean)
        self._request_update.set()

    @property
    def lim_left(self):
        return self._axes.get_xlim()[0]

    @lim_left.setter
    def lim_left(self, limit):

        if not isinstance(limit, (int, float)):
            raise TypeError('not int or float')

        if limit == self.lim_right:
            raise ValueError('left and right limits are identical.')

        self._axes.set_xlim(left=limit)
        self._request_update.set()

    @property
    def lim_right(self):
        return self._axes.get_xlim()[1]

    @lim_right.setter
    def lim_right(self, limit):

        if not isinstance(limit, (int, float)):
            raise TypeError('not int or float')

        if limit == self.lim_left:
            raise ValueError('left and right limits are identical.')

        self._axes.set_xlim(right=limit)
        self._request_update.set()

    @property
    def inverted(self):
        return self.lim_left > self.lim_right

    @inverted.setter
    def inverted(self, boolean):

        if boolean:
            if self.inverted:
                return
        else:
            if not self.inverted:
                return

        autoscale = self.autoscale
        self._axes.invert_xaxis()
        self.autoscale = autoscale
        self._request_update.set()

    @property
    def ticks(self):
        return self._axes.get_xticks()

    @ticks.setter
    def ticks(self, ticks):
        self._axes.set_xticks(ticks)
        self._request_update.set()

    @property
    def scale(self):
        return self._scale

    @property
    def log(self):
        if self._scale == 'log':
            return True
        else:
            return False

    @log.setter
    def log(self, log):

        # Check for bool type
        if not isinstance(log, bool):
            raise TypeError('not bool')

        if log:
            self._scale = 'log'
        else:
            self._scale = 'linear'

        self._request_update.set()


class YaxisConf(object):

    def __init__(self, axes, request_update):
        self._axes = axes
        self._request_update = request_update
        self._scale = 'linear'

    @property
    def autoscale(self):
        return self._axes.get_autoscaley_on()

    @autoscale.setter
    def autoscale(self, boolean):

        # Check for bool type
        if not isinstance(boolean, bool):
            raise TypeError('not bool')

        self._axes.set_autoscaley_on(boolean)
        self._request_update.set()

    @property
    def lim_botton(self):
        return self._axes.get_ylim()[0]

    @lim_botton.setter
    def lim_botton(self, limit):

        if not isinstance(limit, (int, float)):
            raise TypeError('not int or float')

        if limit == self.lim_top:
            raise ValueError('bottom and top limits are identical.')

        self._axes.set_ylim(bottom=limit)
        self._request_update.set()

    @property
    def lim_top(self):
        return self._axes.get_ylim()[1]

    @lim_top.setter
    def lim_top(self, limit):

        if not isinstance(limit, (int, float)):
            raise TypeError('not int or float')

        if limit == self.lim_bottom:
            raise ValueError('left and right limits are identical.')

        self._axes.set_ylim(top=limit)
        self._request_update.set()

    @property
    def inverted(self):
        return self.lim_botton > self.lim_top

    @inverted.setter
    def inverted(self, boolean):

        if boolean:
            if self.inverted:
                return
        else:
            if not self.inverted:
                return

        autoscale = self.autoscale
        self._axes.invert_yaxis()
        self.autoscale = autoscale

        self._request_update.set()

    @property
    def ticks(self):
        return self._axes.get_yticks()

    @ticks.setter
    def ticks(self, ticks):
        self._axes.set_yticks(ticks)
        self._request_update.set()

    @property
    def scale(self):
        return self._scale

    @property
    def log(self):
        if self._scale == 'log':
            return True
        else:
            return False

    @log.setter
    def log(self, log):

        # Check for bool type
        if not isinstance(log, bool):
            raise TypeError('not bool')

        if log:
            self._scale = 'log'
        else:
            self._scale = 'linear'

        self._request_update.set()


class Dataplot1d(DataplotBase):

    def __init__(self, graph, axes, length, continuously=False):
        """Initiate Dataplot1d class.

        """

        DataplotBase.__init__(self, graph, axes)

        # Create emtpy line instance for axes
        self._line, = self._axes.plot([], [])

        # Attributes for displayed number of points
        self._length = length
        self._continuously = continuously

        # Create list to contain plotting data
        self._xdata = list()
        self._ydata = list()

        # Dataplot1d Options
        self._line_conf = LineConf(self._graph, self._line)
        self._marker_conf = MarkerConf(self._graph, self._line)
        self._xaxis_conf = XaxisConf(self._axes, self._request_update)
        self._yaxis_conf = YaxisConf(self._axes, self._request_update)
        self._label_conf = LabelConf1d(self._graph, self._axes)

    @property
    def line(self):
        """Line options.

        """
        return self._line_conf

    @property
    def marker(self):
        """Marker options.

        """

        return self._marker_conf

    @property
    def xaxis(self):
        """Xaxis options.

        """

        return self._xaxis_conf

    @property
    def yaxis(self):
        """Yaxis options.

        """

        return self._yaxis_conf

    @property
    def label(self):
        """Label options.

        """

        return self._label_conf

    @property
    def length(self):
        """Length of displayed datapoints.

        If continuously plotting is off Dataplot1d gets cleared when the number
        of added datapoints matches length. Otherwise this is the maximum
        number of displayed datapoints.

        """
        return self._length

    @property
    def continuously(self):
        """Set continuously plotting True or False.

        If continuously plotting is True Dataplot1d gets cleared when the
        number of added datapoints matches length.

        """
        return self._continuously

    def add_data(self, xdata, ydata):
        """Add a list of data to the plot.

        """

        # Put the incoming data into the data exchange queue
        self._exchange_queue.put([xdata, ydata])

    def _update(self):
        """Update the dataplot with the incoming data.

        Process the added data, handle the maximum number of displayed
        datapoints and manage view limits.
        The _update method is called by the Gaph build method and should not be
        called directly.

        """

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
            self._request_update.set()

        # Update the line with the new data if available
        if self._request_update.is_set():

            xdata = np.array(self._xdata)
            ydata = np.array(self._ydata)

            # Prepare displayed xdata
            if self.xaxis.log:
                xdata = np.abs(self._xdata)

            # Prepare displayed ydata
            if self.yaxis.log:
                ydata = np.abs(self._ydata)

            # Update displayed data.
            self._line.set_data(xdata, ydata)

            # Recompute the data limits.
            self._axes.relim()

            # Set the xaxis scale
            xscale = self.xaxis.scale
            try:
                self._axes.set_xscale(xscale)
            except ValueError:
                    pass

            # Set the yaxis scale
            yscale = self.yaxis.scale
            try:
                self._axes.set_yscale(yscale)
            except ValueError:
                    pass

            # Resacale the view limits using the previous computed data limit.
            try:
                self._axes.autoscale_view()
            except ValueError:
                pass


class ImageConf(object):

    def __init__(self, image, request_update):
        self._image = image
        self._request_update = request_update
        self._auto_extent = True

    @property
    def interpolation(self):
        """Set the interpolation method the image uses when resizing.

        ACCEPTS: ['nearest' | 'bilinear' | 'bicubic' | 'spline16' |
                  'spline36' | 'hanning' | 'hamming' | 'hermite' | 'kaiser' |
                  'quadric' | 'catrom' | 'gaussian' | 'bessel' | 'mitchell' |
                  'sinc' | 'lanczos' | 'none' |]

        """

        return self._image.get_interpolation()

    @interpolation.setter
    def interpolation(self, interpolation):

        if interpolation not in self._image._interpd:
            raise ValueError('Illegal interpolation string')

        self._image.set_interpolation(interpolation)
        self._request_update.set()

    @property
    def auto_extent(self):
        return self._auto_extent

    @auto_extent.setter
    def auto_extent(self, boolean):

        if not isinstance(boolean, bool):
            raise TypeError('not bool')

        self._auto_extent = boolean

    @property
    def extent(self):
        return self._image.get_extent()

    @extent.setter
    def extent(self, extent):
        self._auto_extent = False
        self._image.set_extent(extent)
        self._request_update.set()


class ColorbarConf(object):

    def __init__(self, image, colorbar, request_update):
        self._image = image
        self._colorbar = colorbar
        self._request_update = request_update
        self._scale = 'linear'

    @property
    def colormap(self):
        return self._image.get_cmap().name

    @colormap.setter
    def colormap(self, colormap):
        self._image.set_cmap(colormap)
        self._request_update.set()

    @property
    def scale(self):
        return self._scale

    @property
    def log(self):
        """Set colorbar to logarithmic scale.

        """

        if self._scale == 'log':
            return True
        else:
            return False

    @log.setter
    def log(self, log):

        if not isinstance(log, bool):
            raise TypeError('is not bool')

        if log:
            self._scale = 'log'
        else:
            self._scale = 'linear'

        self._request_update.set()


class LabelConf2d(LabelConf1d):

    def __init__(self, graph, axes, colorbar, request_update):
        LabelConf1d.__init__(self, graph, axes)
        self._colorbar = colorbar

    @property
    def zaxis(self):
        return self._colorbar._label

    @zaxis.setter
    def zaxis(self, string):
        self._colorbar.set_label(string)
        self._request_update.set()


class Dataplot2d(DataplotBase):

    def __init__(self, graph, axes, length):
        DataplotBase.__init__(self, graph, axes)

        self._length = length

        self._exchange_queue = Queue()
        self._data = [[]]

        # Draw an empty image
        self._image = self._axes.imshow([[np.nan]])
        self._axes.set_aspect('auto')

        # Divide axes to fit colorbar (this works but don't aks me why)
        # http://matplotlib.org/examples/axes_grid/demo_axes_divider.html
        axes_divider = make_axes_locatable(self._axes)
        axes_cb = axes_divider.append_axes("right", size="2.5%", pad=0.05)

        # Create colorbar and ignor warning caused because figure has only
        # one value.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._colorbar = self._graph._figure.colorbar(self._image, axes_cb)

        #self._axes.set_axis_off()

        self._image_conf = ImageConf(self._image, self._request_update)
        self._label_conf = LabelConf2d(self._graph, self._axes, self._colorbar,
                                       self._request_update)
        self._colorbar_conf = ColorbarConf(self._image, self._colorbar,
                                           self._request_update)

    @property
    def image(self):
        return self._image_conf

    @property
    def colorbar(self):
        """Colorbar options.

        """

        return self._colorbar_conf

    @property
    def label(self):
        """Label options.

        """

        return self._label_conf

    def add_data(self, data):

        # Put the incoming data into the data exchange queue
        self._exchange_queue.put([data])

    def next_line(self):

        # Put a 'next' meassage into the data exchange queue
        self._exchange_queue.put('next')

    def _update(self):

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
                    self._request_update.set()
                elif message == 'next':
                    self._data.append([])

            # Handle the maximum number of displayed points.
            while len(self._data[-1]) >= self._length:

                split = self._data[-1][self._length:]
                del self._data[-1][self._length:]
                self._data.append(split)

                #Set the up_to_date flag to True for redrawing
                self._request_update.set()

        # Update the image with the new data if available
        if self._request_update.is_set():

            # Prepare displayed data
            data = np.array(self._data[:-1])

            # Take absolute value if log scaled
            if self.colorbar.log:
                data = np.abs(data)

            if self.colorbar.scale == 'linear':
                self._colorbar.set_norm(Normalize())
                self._image.set_norm(Normalize())
            elif self.colorbar.scale == 'log':
                    self._colorbar.set_norm(LogNorm())

            # Set image data
            try:
                self._image.set_data(data)

                # Extent image automaticaly
                if self.image.auto_extent:
                    extent = [0, self._length, len(data), 0]
                    self._image.set_extent(extent)

            except TypeError:
                self._image.set_data([[np.nan]])
                self._axes.set_xticks([])
                self._axes.set_yticks([])

            # Resacale the image
            try:
                self._image.autoscale()
            except ValueError:
                pass
