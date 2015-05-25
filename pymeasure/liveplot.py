# -*- coding: utf-8 -*

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

# Pymeasure
from pymeasure.indexdict import IndexDict

import abc
import sys
import tkinter as Tk
import warnings
import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.colors import Normalize, LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from queue import Queue
from threading import Event
from functools import partial


class LiveGraphBase(IndexDict):
    """Base class for differnt graphic backends.

    """

    def __init__(self, figure=None):
        """Initiate LivegraphBase class.

        Keyword arguments:
        figure -- Can take an instance of matplotlib.figure.Figure otherwise it
                  will be created.

        """

        super().__init__()

        # Define matplotlib Figure
        if figure is None:
            self.figure = mpl.figure.Figure()
        else:
            self.figure = figure

        # Task queue
        self._tasks = Queue()
        self._tight_layout = True
        self.close_event = None

        self._draw = True

    def __setitem__(self, key, dataplot):
        """x.__setitem__(key, dataplot) <==> x['key'] = dataplot

        Add a Dataplot to Graph.
        """

        if isinstance(dataplot, DataplotBase):
            super().__setitem__(key, dataplot)
        else:
            raise TypeError('item must be a Dataplot.')

    def dataplots(self):
        """Return a list of (index, key) pairs in Graph.

        """

        return [index_key for index_key in enumerate(self._odict.keys())]

    def add_subplot(self, *args, **kwargs):
        """Wrapper for matplotlib.figure.add_subplot(*args, **kwargs)

        """

        return self.figure.add_subplot(*args, **kwargs)

    def subplot_grid(self, ysubs, xsubs):
        """ Create a grid of subplots and return all axes in a list.

        """

        axes = []
        for nr in range(1, ysubs * xsubs + 1):
            axes.append(self.add_subplot(ysubs, xsubs, nr))
        return axes

    @property
    def draw(self):
        return self._draw

    @draw.setter
    def draw(self, boolean):
        if isinstance(boolean, bool):
            self._draw = boolean
        else:
            raise TypeError('not boolean type')

    @property
    def visible(self):
        return True

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
        while not self._tasks.empty():
            task = self._tasks.get()
            task()
            self._tasks.task_done()
            up_to_date = False

        for subplot in self.__iter__():
            if subplot._request_update.is_set():
                subplot._update()
                subplot._request_update.clear()
                up_to_date = False

        # Redraw the canvas if up_to_data and visible
        if not up_to_date and self.draw and self.visible:

            # Use tight layout
            if self._tight_layout:
                self.figure.tight_layout()

            # Redraw the graph
            self.figure.canvas.draw()

    @property
    def tight_layout(self):
        return self._tight_layout

    @tight_layout.setter
    def tight_layout(self, boolean):

        # Check for bool type
        if not isinstance(boolean, bool):
            raise TypeError('not bool')

        self._tight_layout = boolean

    def snapshot(self, filename):
        """Make a snapshot and save it as filename.

        """
        task = partial(self.figure.savefig, filename)
        self._graph._tasks.put(task)


class LiveGraphTk(LiveGraphBase):
    """ LiveGraph backend for Tkinter.

    """

    def __init__(self, figure=None, master=None):
        super().__init__(figure)

        # Setup the TKInter window with the canvas and a toolbar
        if not master:
            self._master = Tk.Tk()
        else:
            self._master = master

        # build canvas for Tk
        canvas = FigureCanvasTkAgg(self.figure, master=self._master)
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # Navigation Toolbar
        self._toolbar = NavigationToolbar2TkAgg(canvas, self._master)
        self._toolbar.update()
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # Menubar
        menubar = Tk.Menu(self._master)
        menubar.add_command(label='hide', command=self.hide)
        self._master.config(menu=menubar)

        # Close every
        self._master.protocol("WM_DELETE_WINDOW", self.close)

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

    @property
    def visible(self):
        if self._master.state() in ['normal', 'zoomed']:
            return True
        else:
            return False

    @visible.setter
    def visible(self, boolean):
        if boolean:
            self._master.deiconify()
        else:
            self._master.withdraw()

    def hide(self):
        self.visible = False

    def close(self):
        if self.close_event:
            self.close_event()
        self._master.destroy()


class DataplotBase(object, metaclass=abc.ABCMeta):

    def __init__(self, graph, axes):
        """Initiate DataplotBase class.

        """

        self._graph = graph

        # Check for integer like 221 and handle sequences (2,2,1)
        if not isinstance(axes, mpl.axes.SubplotBase):
            if isinstance(axes, int):
                axes = tuple([int(c) for c in str(axes)])
            axes = self._graph.add_subplot(*axes)

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
        self._graph._tasks.put(partial(self._axes.set_title, string))

    @property
    def xaxis(self):
        return self._axes.get_xlabel()

    @xaxis.setter
    def xaxis(self, string):
        self._graph._tasks.put(partial(self._axes.set_xlabel, string))

    @property
    def yaxis(self):
        return self._axes.get_ylabel()

    @yaxis.setter
    def yaxis(self, string):
        task = partial(self._axes.set_ylabel, string)
        self._graph._tasks.put(task)


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
        if linestyle not in list(self._line.lineStyles.keys()):
            raise ValueError('not a valid linestyle')

        task = partial(self._line.set_linestyle, linestyle)
        self._graph._tasks.put(task)

    @property
    def draw(self):
        return self._line.get_drawstyle()

    @draw.setter
    def draw(self, drawstyle):

        # Handle wrong input to avoid crashing running liveplot
        if drawstyle not in self._line.drawStyleKeys:
            raise ValueError('not a valid drawstyle')

        task = partial(self._line.set_drawstyle, drawstyle)
        self._graph._tasks.put(task)

    @property
    def color(self):
        return self._line.get_color()

    @color.setter
    def color(self, color):

        # Handle wrong input to avoid crashing running liveplot
        if not mpl.colors.is_color_like(color):
            raise ValueError('not a valid color')

        task = partial(self._line.set_color, color)
        self._graph._tasks.put(task)

    @property
    def width(self):
        return self._line.get_linewidth()

    @width.setter
    def width(self, linewidth):

        # Handle wrong input to avoid crashing running liveplot
        linewidth = float(linewidth)
        task = partial(self._line.set_linewidth, linewidth)
        self._graph._tasks.put(task)


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
        elif marker not in list(self._line.markers.keys()):
            raise ValueError('not a valid marker')

        task = partial(self._line.set_marker, marker)
        self._graph._tasks.put(task)

    @property
    def color(self):
        return [self.facecolor, self.edgecolor]

    @color.setter
    def color(self, color):
        if not mpl.colors.is_color_like(color):
            raise ValueError('not a valid color')

        self.facecolor = color
        self.edgecolor = color

    @property
    def facecolor(self):
        return self._line.get_markerfacecolor()

    @facecolor.setter
    def facecolor(self, color):

        # Handle wrong input to avoid crashing running liveplot
        if not mpl.colors.is_color_like(color):
            raise ValueError('not a valid color')

        task = partial(self._line.set_markerfacecolor, color)
        self._graph._tasks.put(task)

    @property
    def edgecolor(self):
        return self._line.get_markeredgecolor()

    @edgecolor.setter
    def edgecolor(self, color):

        # Handle wrong input to avoid crashing running liveplot
        if not mpl.colors.is_color_like(color):
            raise ValueError('not a valid color')

        task = partial(self._line.set_markeredgecolor, color)
        self._graph._tasks.put(task)

    @property
    def size(self):
        return self._line.get_markersize()

    @size.setter
    def size(self, markersize):

        # Handle wrong input to avoid crashing running liveplot
        markersize = float(markersize)

        task = partial(self._line.set_markersize, markersize)
        self._graph._tasks.put(task)


class XaxisConf(object):

    def __init__(self, graph, axes):
        self._graph = graph
        self._axes = axes
        self._scale = 'linear'

    @property
    def autoscale(self):
        return self._axes.get_autoscalex_on()

    @autoscale.setter
    def autoscale(self, boolean):

        # Check for bool type
        if not isinstance(boolean, bool):
            raise TypeError('not bool')

        task = partial(self._axes.set_autoscalex_on, boolean)
        self._graph._tasks.put(task)

    @property
    def lim_left(self):
        return self._axes.get_xlim()[0]

    @lim_left.setter
    def lim_left(self, limit):

        if not isinstance(limit, (int, float)):
            raise TypeError('not int or float')

        if limit == self.lim_right:
            raise ValueError('left and right limits are identical.')

        task = partial(self._axes.set_xlim, left=limit)
        self._graph._tasks.put(task)

    @property
    def lim_right(self):
        return self._axes.get_xlim()[1]

    @lim_right.setter
    def lim_right(self, limit):

        if not isinstance(limit, (int, float)):
            raise TypeError('not int or float')

        if limit == self.lim_left:
            raise ValueError('left and right limits are identical.')

        task = partial(self._axes.set_xlim, right=limit)
        self._graph._tasks.put(task)

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

        def task():
            self._axes.invert_xaxis()
            self._axes.set_autoscalex_on(autoscale)
        self._graph._tasks.put(task)

    @property
    def ticks(self):
        return self._axes.get_xticks()

    @ticks.setter
    def ticks(self, ticks):
        task = partial(self._axes.set_xticks, ticks)
        self._graph._tasks.put(task)

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

    def __init__(self, graph, axes):
        self._graph = graph
        self._axes = axes
        self._scale = 'linear'

    @property
    def autoscale(self):
        return self._axes.get_autoscaley_on()

    @autoscale.setter
    def autoscale(self, boolean):

        # Check for bool type
        if not isinstance(boolean, bool):
            raise TypeError('not bool')

        task = partial(self._axes.set_autoscaley_on, boolean)
        self._graph._tasks.put(task)

    @property
    def lim_bottom(self):
        return self._axes.get_ylim()[0]

    @lim_bottom.setter
    def lim_bottom(self, limit):

        if not isinstance(limit, (int, float)):
            raise TypeError('not int or float')

        if limit == self.lim_top:
            raise ValueError('bottom and top limits are identical.')

        task = partial(self._axes.set_ylim, bottom=limit)
        self._graph._tasks.put(task)

    @property
    def lim_top(self):
        return self._axes.get_ylim()[1]

    @lim_top.setter
    def lim_top(self, limit):

        if not isinstance(limit, (int, float)):
            raise TypeError('not int or float')

        if limit == self.lim_bottom:
            raise ValueError('left and right limits are identical.')

        task = partial(self._axes.set_ylim, top=limit)
        self._graph._tasks.put(task)

    @property
    def inverted(self):
        return self.lim_bottom > self.lim_top

    @inverted.setter
    def inverted(self, boolean):

        if boolean:
            if self.inverted:
                return
        else:
            if not self.inverted:
                return

        autoscale = self.autoscale

        def task():
            self._axes.invert_yaxis()
            self._axes.set_autoscaley_on(autoscale)
        self._graph._tasks.put(task)

    @property
    def ticks(self):
        return self._axes.get_yticks()

    @ticks.setter
    def ticks(self, ticks):
        task = partial(self._axes.set_yticks, ticks)
        self._graph._tasks.put(task)

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


class Dataplot1d(DataplotBase):

    def __init__(self, graph, axes, length=None, continuously=False):
        """Initiate Dataplot1d class.

        """
        super().__init__(graph, axes)

        # Create emtpy line instance for axes
        self._line, = self._axes.plot([], [])

        # Attributes for displayed number of points
        self._length = length
        self._continuously = continuously

        # Create list to contain plotting data
        self._xdata = list()
        self._ydata = list()

        # Dataplot1d Configs
        self._line_conf = LineConf(self._graph, self._line)
        self._marker_conf = MarkerConf(self._graph, self._line)
        self._xaxis_conf = XaxisConf(self._graph, self._axes)
        self._yaxis_conf = YaxisConf(self._graph, self._axes)
        self._label_conf = LabelConf1d(self._graph, self._axes)

        self.switch_xy = False

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

    @property
    def switch_xy(self):
        return self._xy_switch

    @switch_xy.setter
    def switch_xy(self, boolean):
        self._xy_switch = bool(boolean)

    def add_data(self, xdata, ydata):
        """Add a list of data to the plot.

        """

        # Put the incoming data into the data exchange queue
        task = partial(self._add_data, xdata, ydata)
        self._graph._tasks.put(task)

    def _add_data(self, xdata, ydata):
        if self._length:
            self._xdata.extend(xdata)
            self._ydata.extend(ydata)

            # Clear if data is to long
            while len(self._xdata) > self._length:
                # Remove oldest datapoints if plotting continuously.
                if self._continuously:
                    del self._xdata[:-self._length]
                    del self._ydata[:-self._length]

                # Clear all displayed datapoints otherwise.
                else:
                    del self._xdata[:self._length]
                    del self._ydata[:self._length]

        else:
            self._xdata = xdata
            self._ydata = ydata

        self._request_update.set()

    def _update(self):
        """Update the dataplot with the incoming data.

        Process the added data, handle the maximum number of displayed
        datapoints and manage view limits.
        The _update method is called by the Gaph build method and should not be
        called directly.

        """

        xdata = np.array(self._xdata)
        ydata = np.array(self._ydata)

        # Prepare displayed xdata
        if self.xaxis.log:
            xdata = np.abs(xdata)

        # Prepare displayed ydata
        if self.yaxis.log:
            ydata = np.abs(ydata)

        # Update displayed data.
        if not self.switch_xy:
            self._line.set_data(xdata, ydata)
        else:
            self._line.set_data(ydata, xdata)

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

    def __init__(self, graph, image):
        self._graph = graph
        self._image = image
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

        task = partial(self._image.set_interpolation, interpolation)
        self._graph._tasks.put(task)

    @property
    def auto_extent(self):
        return self._auto_extent

    @auto_extent.setter
    def auto_extent(self, boolean):

        # Check for bool type
        if not isinstance(boolean, bool):
            raise TypeError('not bool')

        self._auto_extent = boolean

    @property
    def extent(self):
        return self._image.get_extent()

    @extent.setter
    def extent(self, extent):
        self._auto_extent = False
        task = partial(self._image.set_extent, extent)
        self._graph._tasks.put(task)


class ColorbarConf(object):

    def __init__(self, graph, image, colorbar):
        self._graph = graph
        self._image = image
        self._colorbar = colorbar
        self._scale = 'linear'

    @property
    def colormap_names(self):
        return sorted(mpl.cm.cmap_d.keys())

    @property
    def colormap(self):
        return self._image.get_cmap().name

    @colormap.setter
    def colormap(self, colormap):
        if colormap not in self.colormap_names:
            raise TypeError('colormap is not valid')

        task = partial(self._image.set_cmap, colormap)
        self._graph._tasks.put(task)

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


class LabelConf2d(LabelConf1d):

    def __init__(self, graph, axes, colorbar):
        super().__init__(graph, axes)
        self._colorbar = colorbar

    @property
    def zaxis(self):
        return self._colorbar._label

    @zaxis.setter
    def zaxis(self, string):
        task = partial(self._colorbar.set_label, string)
        self._graph._tasks.put(task)


class Dataplot2d(DataplotBase):

    def __init__(self, graph, axes, length):
        super().__init__(graph, axes)

        self._length = length

        self._exchange_queue = Queue()
        self._trace = []
        self._data = np.array([[]])

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
            self._colorbar = self._graph.figure.colorbar(self._image, axes_cb)

        self._image_conf = ImageConf(self._graph, self._image)
        self._label_conf = LabelConf2d(self._graph, self._axes, self._colorbar)
        self._colorbar_conf = ColorbarConf(self._graph, self._image,
                                           self._colorbar)
        self._colorbar_conf.colormap = 'hot'
        self._diff = False

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

    @property
    def diff(self):
        return self._diff

    @diff.setter
    def diff(self, diff):
        if int(diff) > 0:
            self._diff = int(diff)
        elif diff is False:
            self._diff = False
        else:
            raise ValueError('diff musste be True, False or integer greater 0')

    def add_data(self, data):
        """Add a list of data to the plot.

        """
        task = partial(self._add_data, data)
        self._graph._tasks.put(task)

    def _add_data(self, data):

        if isinstance(data, Dataplot1d):
            self._trace.extend(data._ydata)
        else:
            self._trace.extend(data)

        # Handle the maximum number of displayed points.
        while len(self._trace) >= self._length:

            trace = self._trace[:self._length]
            del self._trace[:self._length]

            if self._data.size:
                self._data = np.vstack((self._data, trace))
            else:
                self._data = np.array([trace])

        self._request_update.set()

    def new_line(self):
        self._graph._tasks.put(self._clear)

    def _new_line(self):
        self._data.append([])
        self._request_update.set()

    def clear(self):
        self._graph._tasks.put(self._clear)

    def _clear(self):
        self._data = np.array([[]])
        self._request_update.set()

    def _update(self):

        # Prepare displayed data
        data = self._data.copy()

        # Differentiate data
        if self.diff:
            data = data[:, self.diff:] - data[:, :-self.diff]

        # Take absolute value if log scaled
        if self.colorbar.log:
            data[data <= 0] = np.nan

        if self.colorbar.scale == 'linear':
            self._colorbar.set_norm(Normalize())
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
