# -*- coding: utf-8 -*-

from pymeasure.indexdict import IndexDict
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtGui, QtCore
from queue import Queue
import numpy as np
from functools import partial
from scipy.ndimage.interpolation import zoom

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class Manager:
    """Manager handels all graph changes sequential.

    """

    graphicswindow = None
    plotitem = None

    def __init__(self):
        self.tasks = Queue()
        self.running = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.process)

    @staticmethod
    def task(method):
        """Task decorator.
        """

        def task_method(self, *args, **kwargs):
            task = (self, partial(method, self, *args, **kwargs))
            self._manager.tasks.put(task)

        return task_method

    def process(self):
        """Process the all task in the input queue
        """

        self.graphs = []

        # Execute all tasks
        while not self.tasks.empty():
            graph, task = self.tasks.get()
            task()
            self.tasks.task_done()

            if graph not in self.graphs:
                self.graphs.append(graph)

        for graph in self.graphs:
            try:
                graph.update()
            except AttributeError:
                pass

    def start(self, interval):
        self.timer.start(interval)

    def stop(self):
        self.timer.stop()


class LiveGraph(IndexDict):

    def __init__(self, title=None, size=(1024,800), view='normal', manager=None, **kargs):
        super().__init__()

        if manager:
            self._manager = manager
        else:
            self._manager = Manager()

        self._gwin = pg.GraphicsWindow(title, size, **kargs)
        Manager.graphicswindow = self

        self._gwin.closeEvent = self._close_event
        self.show(view)

    def _close_event(self, event):

        # Pop up quit message box on exit
        reply = QtGui.QMessageBox.question(self._gwin, 'Quit', "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self._manager.timer.stop()
            event.accept()
        else:
            event.ignore()

    def run(self, interval=50):
        self._manager.start(interval)

    def next_col(self):
        self._gwin.nextCol()

    def next_row(self):
        self._gwin.nextRow()

    def add_plot(self, *args, **kwargs):
        plotitem = self._gwin.addPlot(*args, **kwargs)
        return plotitem

    @property
    def title(self):
        return self._gwin.windowTitle()

    @title.setter
    @Manager.task
    def title(self, title):
        self._gwin.setWindowTitle(title)

    def show(self, view='normal'):
        if view == 'normal':
            self._gwin.showNormal()
        elif view == 'max':
            self._gwin.showMaximized()
        elif view == 'min':
            self._gwin.showMinimized()
        elif view == 'full':
            self._gwin.showFullScreen()
        elif view == 'hide':
            self._gwin.hide()
        else:
            raise KeyError()

    @property
    def size(self):
        width = self._gwin.size().width()
        height = self._gwin.size().height()
        return (width, height)

    @size.setter
    @Manager.task
    def size(self, size):
        self._gwin.resize(*size)

    @Manager.task
    def screenshot(self, filename=None, copy=False):
        pg.exporters.ImageExporter(self._gwin.scene()).export(fileName=filename, toBytes=False, copy=copy)


class Line:

    symbol_keys = list(pg.graphicsItems.ScatterPlotItem.Symbols.keys())
    color_keys = list(pg.Colors.keys())

    def __init__(self, *args, length=None, continuously=False, livegraph=None, plotitem=None, **kwargs):

        if livegraph:
            self._graph = livegraph
        else:
            self._graph = Manager.graphicswindow

        if plotitem:
            self._plotitem = plotitem
        else:
            self._plotitem = Manager.graphicswindow.add_plot()

        self._manager = self._graph._manager

        self._curve = self._plotitem.plot(*args, **kwargs)

        # Transform pen string it pen opject
        self._curve.setPen(self._curve.opts['pen'])
        self._curve.setSymbolPen(self._curve.opts['symbolPen'])
        self._curve.setSymbolBrush(self._curve.opts['symbolBrush'])

        self._length = length
        self._continuously = continuously
        self._data = Queue()
        self._xdata = []
        self._ydata = []


    @Manager.task
    def add_data(self, xdata, ydata):
        """Add a list of data to the plot.

        """
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


    def update(self):
        self._curve.setData(np.array(self._xdata), np.array(self._ydata))

    @property
    def grid_x(self):
        return self._plotitem.ctrl.xGridCheck.isChecked()

    @grid_x.setter
    @Manager.task
    def grid_x(self, boolean):
        self._plotitem.showGrid(x=boolean)

    @property
    def grid_y(self):
        return self._plotitem.ctrl.yGridCheck.isChecked()

    @grid_y.setter
    @Manager.task
    def grid_y(self, boolean):
        self._plotitem.showGrid(y=boolean)

    @property
    def grid_xy(self):
        return (self.grid_x, self.grid_y)

    @grid_xy.setter
    @Manager.task
    def grid_xy(self, boolean):
        self._plotitem.showGrid(x=boolean, y=boolean)

    @property
    def autorange_x(self):
        return self._plotitem.vb.autoRangeEnabled()[0]

    @autorange_x.setter
    @Manager.task
    def autorange_x(self, value):
        self._plotitem.vb.enableAutoRange('x', value)

    @property
    def autorange_y(self):
        return self._plotitem.vb.autoRangeEnabled()[1]

    @autorange_y.setter
    @Manager.task
    def autorange_y(self, value):
        self._plotitem.vb.enableAutoRange('y', value)

    @property
    def autorange_xy(self):
        return (self.autorange_x, self.autorange_y)

    @autorange_xy.setter
    @Manager.task
    def autorange_xy(self, value):
        self._plotitem.vb.enableAutoRange('xy', value)

    @property
    def symbol(self):
        return self._curve.opts['symbol']

    @symbol.setter
    @Manager.task
    def symbol(self, symbol):
        self._curve.setSymbol(symbol)

    ### Following methods do not update the graph automatically ###

    @property
    def line_style(self):
        pass

    def _get_color(self, key):
        color = self._curve.opts[key].color()
        for name, pgcolor in pg.Colors.items():
            if color == pgcolor:
                return name
        return color.name()

    def _set_color(self, key, color):
        self._curve.opts[key].setColor(pg.mkColor(color))

    @property
    def line_color(self):
        return self._get_color('pen')

    @line_color.setter
    @Manager.task
    def line_color(self, color):
        self._set_color('pen', color)

    @property
    def line_width(self):
        return self._curve.opts['pen'].width()

    @line_width.setter
    @Manager.task
    def line_width(self, width):
        self._curve.opts['pen'].setWidth(int(width))

    @property
    def symbol_color(self):
        line = self.symbol_line_color
        brush = self.symbol_brush_color
        return (line, brush)

    @symbol_color.setter
    @Manager.task
    def symbol_color(self, color):
        self._set_color('symbolPen', color)
        self._set_color('symbolBrush', color)

    @property
    def symbol_size(self):
        return self._curve.opts['symbolSize']

    @symbol_size.setter
    @Manager.task
    def symbol_size(self, size):
         self._curve.setSymbolSize(size)

    @property
    def symbol_line_color(self):
        return self._get_color('symbolPen')

    @symbol_line_color.setter
    @Manager.task
    def symbol_line_color(self, color):
        self._set_color('symbolPen', color)

    @property
    def symbol_brush_color(self):
        return self._get_color('symbolBrush')

    @symbol_brush_color.setter
    @Manager.task
    def symbol_brush_color(self, color):
        self._set_color('symbolBrush', color)


class Image:

    def __init__(self, *args, length=None, livegraph=None, plotitem=None, sidebar='histogram', colormap='thermal', **kwargs):

        if livegraph:
            self._graph = livegraph
        else:
            self._graph = Manager.graphicswindow

        if plotitem:
            self._plotitem = plotitem
        else:
            self._plotitem = Manager.graphicswindow.add_plot()

        self._manager = self._graph._manager

        # create image item
        self._image = pg.ImageItem()
        self._plotitem.addItem(self._image)


        if sidebar == 'histogram':
            self._hist = pg.HistogramLUTItem()
            self._hist.setImageItem(self._image)
            self._graph._gwin.addItem(self._hist)
            self._gradient = self._hist.gradient
            self.gradient = colormap
        elif sidebar == 'gradient':
            # create and connect gradient colorbar
            self._gradient = pg.GradientEditorItem(orientation='right')
            def update_lut():
                self._image.setLookupTable(self._gradient.getLookupTable(256))
            self._gradient.sigGradientChanged.connect(update_lut)
            self._graph._gwin.addItem(self._gradient)
            self.gradient = colormap
        else:
            pass

        self._length = length
        self._qdata = Queue()
        self._trace = []
        self._data = np.array([[]])

        self._tasks = 0

        self.interpolation_mode = 0
        self.interpolation_zoom = 4

        self.autolevel = True


    @Manager.task
    def add_data(self, data):
        """Add a list of data to the plot.

        """

        if isinstance(data, Line):
            data = data._ydata[:]

        self._trace.extend(data)

        # Handle the maximum number of displayed points.
        while len(self._trace) >= self._length:

            trace = self._trace[:self._length]
            del self._trace[:self._length]

            if self._data.size:
                self._data = np.vstack((self._data, trace))
            else:
                self._data = np.array([trace])



    def update(self):
        if self.interpolation_mode:
            data = zoom(input=self._data, zoom=self.interpolation_zoom, order=self.interpolation_mode)
            self._image.setImage(data.T)
        else:
            self._image.setImage(self._data.T)

        try:
            self._hist.imageChanged(autoLevel=self.autolevel)
            self._hist.regionChanging()
            self._hist.regionChanged()
        except AttributeError:
            pass

    gradient_keys = list(pg.graphicsItems.GradientEditorItem.Gradients.items())

    @property
    def gradient(self):
        self._gradient.getGradient()

    @gradient.setter
    @Manager.task
    def gradient(self, key):
        self._gradient.loadPreset(key)

    @property
    def interpolation_mode(self):
        return self._interpolation_mode

    @interpolation_mode.setter
    @Manager.task
    def interpolation_mode(self, mode):
        self._interpolation_mode = int(mode)

    @property
    def interpolation_zoom(self):
        return self._interpolation_zoom

    @interpolation_zoom.setter
    @Manager.task
    def interpolation_zoom(self, factor):
        self._interpolation_zoom = float(factor)