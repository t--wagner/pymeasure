from collections import OrderedDict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import Tkinter
import time
import Queue
#from functools import wraps

class _IndexDict(object):

    def __init__(self):
        self._odict = OrderedDict()
               
    def __iter__(self):
        return iter(self._odict.items())
       
    def __len__(self):
        return len(self._odict)
          
    def __getitem__(self, key):
        try:
            return self._odict[key]
        except KeyError:
            try:
                key = self._odict.keys()[key]
                return self._odict[key] 
            except:
                raise KeyError
        
    def __setitem__(self, key, item):
        if type(key) is not str:
            raise KeyError, 'key must be str'
        else:
            self._odict[key] = item

    def __delitem__(self, key):
        try:
            del self._odict[key]
        except KeyError:
            try:
                key = self._odict.keys()[key]
                del self._odict[key]
            except:
                raise KeyError
                

class Channel(object):
    
    def __init__(self):
        self._attributes = list()
    
    def __call__(self, *values):
        if len(values) == 0:
            return self.read()
        else:
            return self.write(*values)
        
    def config(self, load=None, save=None):
        if load is not None:
            pass
        elif save is not None:
            pass
        else:
            for attribute in self._attributes:
                print attribute + " = " + str(self.__getattribute__(attribute))
                   
    
class Instrument(_IndexDict):

    def __init__(self):
        _IndexDict.__init__(self)
        
    def __setitem__(self, key, channel):
        if isinstance(channel, Channel):
            _IndexDict.__setitem__(self, key, channel)
        else:
            raise TypeError, 'item must be a Channel.'    
    
    @property        
    def channels(self):
        return [index_key for index_key in enumerate(self._odict.keys())]
              
              
class Rack(_IndexDict):

    def __init__(self):
        _IndexDict.__init__(self)
    
    def __setitem__(self, key, instrument):
        if isinstance(instrument, Instrument):
            _IndexDict.__setitem__(self, key, instrument)
        else:
            return TypeError, 'item must be a Instrument.'

    @property        
    def instruments(self):
        return [index_key for index_key in enumerate(self._odict.keys())]
            
            
class Ramp(object):
    
    def __init__(self, ramprate=None, steptime=None):
        self._ramprate = ramprate
        self._steptime = steptime
        
    @property
    def ramprate(self):
        return self._ramprate
    
    @ramprate.setter
    def ramprate(self, rate):
        self._ramprate = rate          
               
    @property
    def steptime(self):
        return self._steptime
    
    @steptime.setter
    def steptime(self, time):
        self._steptime = time
              
    def _rampdecorator(self, read, write, factor):
        
        def ramp(stop, verbose=False):
            start = read()[0]
            position = start
                       
            try:
                stepsize = abs(self._steptime * self._ramprate * factor)
            except TypeError:
                stepsize = None
                               
            #Calculate number of points
            try:
                points = abs(int(float(stop - start) / stepsize)) + 1
            except TypeError:
                points = 1
            
            #Correction of stepsize
            stepsize = float(stop - start) / points
            
            #Correction of steptime
            try:
                steptime = abs(stepsize / float(self._ramprate * factor))
            except TypeError:
                steptime = 0
            
            start_time = time.time()
            for n, step in ((n, start + n * stepsize) for n in xrange(1, points + 1)):
                #print "step: " + str(step)
                position = write(step)
                if verbose:
                    print position
                    
                wait_time = steptime - (time.time() - start_time)    
                if wait_time > 0:
                    time.sleep(wait_time)
                
                start_time = time.time()
                
                try:
                    pass
                except KeyboardInterrupt:
                    break
                
            return position
                
        return ramp

        
class LinearSweep(object):

    def __init__(self, channel, start, stop, points):
        self._channel = channel
        self._start = start
        self._stop = stop
        self._points = points

    def __iter__(self):
        for step in self.steps:
            yield self._channel.write(step)
                
    def __len__(self):
        return self.points

    @property
    def steps(self):
        return [self.stepsize * n + self._start for n in xrange(self._points)]
    
    @property
    def start(self):
        return self._start
            
    @start.setter
    def start(self, start):
        self._start = start
    
    @property
    def stop(self):
        return self._stop
            
    @stop.setter
    def stop(self, stop):
        self._stop = stop

    @property
    def points(self):
            return self._points
    
    @points.setter
    def points(self, points):
        if type(points) is int:
            self._points = points
        else:
            raise ValueError
    
    @property
    def stepsize(self):
        return (self._stop - self._start) / float(self._points - 1)

    @stepsize.setter
    def stepsize(self, stepsize):
        self._points = int(float((self._stop) - self._start) / stepsize) + 1


class TimeSweep(object):
    
    def __init__(self, time, points):
        
        self._time = time
        self._points = int(points)

    def __iter__(self):
        for step in xrange(self._points):
            time.sleep(self._time)
            yield step
        
    def __len__(self):
        return self._points
        
    @property
    def time(self):
        return self._time
    
    @time.setter
    def time(self, time):
        self._time = time
        
    @property
    def points(self):
        return self._points
    
    @points.setter
    def points(self, points):
        self._points = points
        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
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
            raise TypeError, 'item must be a Dataplot.'    
    
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
        rows = self.__len__()  / self._colums
        if self.__len__()  % self._colums == 0:
            return rows
        else:
            return rows + 1
        
    def save(self, path):
        self._save_path.put(path)
    
    def create(self):
        nr = 1
        for key, dataplot in self.__iter__():
            dataplot.axes = self.figure.add_subplot(self.rows, self._colums, nr)
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
        except TypError:
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
                self._line.set_data(self._xdata, self._ydata[0:len(self._xdata)])
                self._axes.relim()
                self._axes.autoscale_view()
            except AttributeError:
                self._line, = self._axes.plot(self._xdata, self._ydata[0:len(self._xdata)])
        
        # Return the update flag. If 1 it will cause a redraw of the canvas 
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
                    #self._image = self._axes.matshow(self._data, aspect='auto')self._image = self._axes.imshow(self._data[0:-1], aspect='auto')
                    self._image = self._axes.imshow(self._data, aspect='auto')
                    self._axes.set_axis_off()
                    #self._colorbar = colorbar(self._image, ax=self._axes)
                    
                self._data.append([])
                need_update = True
                        
        return need_update