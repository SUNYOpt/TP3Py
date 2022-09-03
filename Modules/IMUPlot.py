from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import random
import json
from collections import namedtuple
import numpy as np

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

global ModuleDir
ModuleDir = "Modules/"

print('yo')

#################################
""" Class we need for plotting"""
#################################
class IMUCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.Accaxes = fig.add_subplot(311)
        self.Gyroaxes = fig.add_subplot(312)
        self.Magaxes = fig.add_subplot(313)

        super(IMUCanvas, self).__init__(fig)
        self.Accaxes.set_ylim(-15, 15)
        self.Accaxes.set_xlabel('time (s)')
        self.Accaxes.set_ylabel('Accelerometer (m/s^2)')

        self.Gyroaxes.set_ylim(-100, 100)
        self.Gyroaxes.set_xlabel('time (s)')
        self.Gyroaxes.set_ylabel('Gyroscope (deg./s)')

        self.Magaxes.set_ylim(-40, 150)
        self.Magaxes.set_xlabel('time (s)')
        self.Magaxes.set_ylabel('Magnetometer (micro Tesla)')
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
class IMUPlot(QObject):

   # Visual Arrangment of the GUI 
   def __init__(self, GstreamWorker):

       super().__init__()

       print('Hey Lets go disco!!')  

       self.window = WindowArrangment()
       self.window.show()
       

       # For now we feed a random data to the module in here!
       n_data = 200
       nmag_data = 50
       self.NumSample = 50
       self.NumMagSample = 5

       self.xdata = [0 for i in range(n_data)]
       self.xmagdata = [0 for i in range(nmag_data)]
       self.ydata = np.zeros((n_data,3))
       self.ydataGyro= np.zeros((n_data,3))
       self.ydataMag= np.zeros((nmag_data,3))

       # We need to store a reference to the plotted line
       # somewhere, so we can apply the new data to it.
       self._plot_ref = [None, None, None]
       self._plot_refGyro = [None, None, None]
       self._plot_refMag = [None, None, None]

       #self.update_plot()

       #self.timer = QtCore.QTimer()
       #self.timer.setInterval(100)
       #self.timer.timeout.connect(self.update_plot)
       #self.timer.start()

       # Connect IMU signals to IMU processor
       self.GstreamWorker = GstreamWorker
       self.GstreamWorker.IMU_signal.connect(self.ProcessIMU)

       self.CurrentAcc = []
       self.CurrentTime = []
       self.CurrentGyro = []

       self.CurrentMag = []
       self.CurrentMagTime = []


   def update_plot(self):
        # Drop off the first y element, append a new one.
        #print(self.CurrentAcc.shape())
        self.ydata = np.concatenate((self.ydata[self.NumSample:,:], np.array(self.CurrentAcc)), axis = 0)
        self.xdata = np.concatenate((self.xdata[self.NumSample:], self.CurrentTime), axis = None)
        ColorChar = ['r', 'g', 'b']
        #print(self.xdata)
        for axis in range(3):
        # Note: we no longer need to clear the axis.
            if self._plot_ref[axis] is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
                plot_refs = self.window.IMUcanvas.Accaxes.plot(self.xdata, self.ydata[:,axis], ColorChar[axis])
                self._plot_ref[axis] = plot_refs[0]
            else:
            # We have a reference, we can use it to update the data for that line.
                self._plot_ref[axis].set_ydata(self.ydata[:,axis])
                self._plot_ref[axis].set_xdata(self.xdata)
                self.window.IMUcanvas.Accaxes.set_xlim(min(self.xdata), max(self.xdata))


        self.ydataGyro = np.concatenate((self.ydataGyro[self.NumSample:,:], np.array(self.CurrentGyro)), axis = 0)
        for axis in range(3):
            if self._plot_refGyro[axis] is None:
                _plot_refGyro = self.window.IMUcanvas.Gyroaxes.plot(self.xdata, self.ydataGyro[:,axis], ColorChar[axis])
                self._plot_refGyro[axis] = _plot_refGyro[0]
            else:
                self._plot_refGyro[axis].set_ydata(self.ydataGyro[:,axis])
                self._plot_refGyro[axis].set_xdata(self.xdata)
                self.window.IMUcanvas.Gyroaxes.set_xlim(min(self.xdata), max(self.xdata))

        # Redraw the canvas
        self.window.IMUcanvas.draw()

        self.CurrentAcc = []
        self.CurrentTime = []
        self.CurrentGyro = []


   def update_Magplot(self):
       # Drop off the first y element, append a new one.
       # print(self.CurrentAcc.shape())
       self.ydataMag = np.concatenate((self.ydataMag[self.NumMagSample:, :], np.array(self.CurrentMag)), axis=0)
       self.xmagdata  = np.concatenate((self.xmagdata[self.NumMagSample:], self.CurrentMagTime), axis=None)
       ColorChar = ['r', 'g', 'b']
       # print(self.xdata)
       for axis in range(3):
           # Note: we no longer need to clear the axis.
           if self._plot_refMag[axis] is None:
               # First time we have no plot reference, so do a normal plot.
               # .plot returns a list of line <reference>s, as we're
               # only getting one we can take the first element.
               _plot_refMag = self.window.IMUcanvas.Magaxes.plot(self.xmagdata, self.ydataMag[:, axis], ColorChar[axis])
               self._plot_refMag[axis] = _plot_refMag[0]
           else:
               # We have a reference, we can use it to update the data for that line.
               self._plot_refMag[axis].set_ydata(self.ydataMag[:, axis])
               self._plot_refMag[axis].set_xdata(self.xmagdata)
               self.window.IMUcanvas.Magaxes.set_xlim(min(self.xdata), max(self.xdata))

       # Redraw the canvas
       self.window.IMUcanvas.draw()

       self.CurrentMagTime = []
       self.CurrentMag = []


   def updateSample(self, acc, time, gyro):
       self.CurrentAcc.append(acc)
       self.CurrentGyro.append(gyro)
       self.CurrentTime.append(time)
       if len(self.CurrentAcc) > self.NumSample:
           self.update_plot()

   def updateMagSample(self, mag, time):
       self.CurrentMag.append(mag)
       self.CurrentMagTime.append(time)
       if len(self.CurrentMag) > self.NumMagSample:
           self.update_Magplot()

   @pyqtSlot(str)
   def ProcessIMU(self, meassage):
       # Check if the data is acc/gyro or mag
       Acc_ind = meassage.find("accelerometer")
       Mag_ind = meassage.find("magnetometer")

       if Acc_ind > 0:

           AccD = json.loads(meassage, object_hook=
           lambda d: namedtuple('X', d.keys())
           (*d.values()))
           #print('time', AccD.tacc, ' acc', AccD.accelerometer[2])
           # self.Acc3D_x.append(AccD.accelerometer[0])
           # self.Acc3D_y.append(AccD.accelerometer[1])
           # self.Acc3D_z.append(AccD.accelerometer[2])
           self.updateSample(AccD.accelerometer, AccD.tacc, AccD.gyroscope)
           # Gyto data
           # self.Gyro3D_x.append(AccD.gyroscope[0])
           # self.Gyro3D_y.append(AccD.gyroscope[1])
           # self.Gyro3D_z.append(AccD.gyroscope[2])

           # self.IMU_time.append(IMUtime)

       if Mag_ind > 0:

           MagD = json.loads(meassage, object_hook=
           lambda d: namedtuple('X', d.keys())
           (*d.values()))

           self.updateMagSample(MagD.magnetometer,MagD.tmag)

   def close(self):
        # Closing the window
        self.window.close()
