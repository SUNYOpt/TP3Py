from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import random


global ModuleDir
ModuleDir = "Modules/"

print('yo')

#################################
""" Class we need for plotting"""
#################################
class IMUCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(IMUCanvas, self).__init__(fig)


########################################################################
#Visual arrangment and the things we'd like to have on the module's GUI#
########################################################################
class WindowArrangment(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Random Plot')
        #self.setFixedSize(1200, 600)

        # Set the central widget
        self._centralWidget = QWidget(self)
        self.generalLayout =  QGridLayout()
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self.IMUcanvas = IMUCanvas(self, width=5, height=4, dpi=100)
        self.generalLayout.addWidget(self.IMUcanvas, 1, 1)


######################################################
#The Class definition that we load in the main thread#
######################################################
class RandomPlot():

   # Visual Arrangment of the GUI 
   def __init__(self):

       super().__init__()

       print('Hey Lets go disco!!')  

       self.window = WindowArrangment()
       self.window.show()
       

       # For now we feed a random data to the module in here!
       n_data = 50
       self.xdata = list(range(n_data))
       self.ydata = [random.randint(0, 10) for i in range(n_data)]       
       # We need to store a reference to the plotted line
       # somewhere, so we can apply the new data to it.
       self._plot_ref = None
       self.update_plot()

       self.timer = QtCore.QTimer()
       self.timer.setInterval(100)
       self.timer.timeout.connect(self.update_plot)
       self.timer.start()

      
   def update_plot(self):
        # Drop off the first y element, append a new one.
        self.ydata = self.ydata[1:] + [random.randint(0, 10)]

        # Note: we no longer need to clear the axis.
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.window.IMUcanvas.axes.plot(self.xdata, self.ydata, 'r')
            self._plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_ydata(self.ydata)

        # Trigger the canvas to update and redraw.
        self.window.IMUcanvas.draw()