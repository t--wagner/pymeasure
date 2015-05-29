import random
from PyQt4 import QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyDynamicMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        #self.axes0.hold(False)
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(10000)

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l0 = [random.randint(0, 10) for i in range(20)]
        self.axes.plot(range(20), l0, c='g')
        self.draw()



#qApp = QtGui.QApplication(sys.argv)

aw = MyDynamicMplCanvas()
aw.show()
#sys.exit(qApp.exec_())
#qApp.exec_()