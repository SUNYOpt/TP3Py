#HRN 07/09/21
#

# importing the module
import json
from collections import namedtuple
import matplotlib.animation as animation
import sys
import os
import cv2
import numpy

import glob
import importlib

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random
from PyQt5 import QtCore
from queue import Queue


import struct
import math 
# 1. Import `QApplication` and all the required widgets
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap

from PyQt5 import QtWidgets

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from functools import partial
from datetime import datetime
from TobiiExtract import TobiiExtract
from TP3py_Gstream import TP3py_Gstream

global ModuleDir
ModuleDir = "Modules/"

class ModuleHandler():

   def __init__(self):
        super().__init__()     
        module_classes = []
  
   def ModuleInit(self, Mod_names):
        global ModuleDir
        moduleList = glob.glob(ModuleDir+"*.py") 

        sys.path.append(ModuleDir)

        print(moduleList)
        for currName in moduleList:

            module  = __import__(currName[len(ModuleDir):])

            cls = getattr(module, currName[len(ModuleDir):])

            print (currName)


   # Starting the modules
   #def ModuleStart(self):
   # Ending the module's functions
   def ModuleEnd(self):
        print('end')

# Create a subclass of QMainWindow 
class TobiiRecUI(QMainWindow):
   global ModuleDir

   stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread

   def __init__(self):
        super().__init__()
        # Set some main window's properties
        self.setWindowTitle('Tobii 3 Recorder')
        #self.setFixedSize(1200, 600)
        # Set the central widget
        self._centralWidget = QWidget(self)
        self.generalLayout =  QGridLayout()
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        
        self.startbutton = QPushButton('start experiment')
        self.endbutton = QPushButton('end experiment')

        self.generalLayout.addWidget(QLabel('<h2>Experiment Name:</h2>'), 0, 0)
        self.generalLayout.addWidget(QLineEdit(), 0, 1)
        self.generalLayout.addWidget(self.startbutton, 1, 0)
        self.generalLayout.addWidget(self.endbutton, 1, 1)        
        
        self.generalLayout.addWidget(QLabel('Elapsed time:'), 2, 0)
        self.ElapsedTimedisplay = QLineEdit()
        self.generalLayout.addWidget(self.ElapsedTimedisplay, 2, 1)
        #self.ElapsedTimedisplay.setText("hmm")


        
        self.thread = QThread()
        self.GstreamWorker = TP3py_Gstream()

        self.ModuleHandler = ModuleHandler()

        self.stop_signal.connect(self.GstreamWorker.stop)  # connect stop signal to worker stop method
        self.GstreamWorker.moveToThread(self.thread)

        self.GstreamWorker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.GstreamWorker.finished.connect(self.GstreamWorker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread
        
        self.ElapsedTimedisplay.textChanged.connect(self.nameEcho)
        
        self.thread.started.connect(self.GstreamWorker.do_work)
        self.thread.finished.connect(self.GstreamWorker.stop)

        # Start Button action:
        self.startbutton.clicked.connect(self.thread.start)

        # Stop Button action:
        self.endbutton.clicked.connect(self.stop_thread)        


        self.listwidget = QListWidget()
        self.listwidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        self.generalLayout.addWidget(self.listwidget, 2, 2)

        moduleList = glob.glob(ModuleDir+"*.py") 


        # add some items
        for i in moduleList:
            it = QtWidgets.QListWidgetItem(i)
            self.listwidget.addItem(it)
            it.setSelected(True)

        self.listwidget.itemClicked.connect(self.printItemText)
        # selected items
        for item in self.listwidget.selectedItems():
            print(item.text())

        
    # When stop_btn is clicked this runs. Terminates the worker and the thread.
   def stop_thread(self):
        self.stop_signal.emit()  # emit the finished signal on stop

   def nameEcho (self):
        print("here setting name: "+ self.ElapsedTimedisplay.text())
        global namestring
        namestring = self.ElapsedTimedisplay.text()
    
   def printItemText(self):       
        items = self.listwidget.selectedItems()
        x = []
        for i in range(len(items)):
            x.append(str(self.listwidget.selectedItems()[i].text()))

        #print (x)
        self.ModuleHandler.ModuleInit(x)

def main():
    """Main function."""
    # Create an instance of QApplication
    TobiiRecApp = QApplication(sys.argv)
    # Show the TobiiRec GUI
    view = TobiiRecUI()
    view.show()


    # Execute the application's main loop
    sys.exit(TobiiRecApp.exec_())

if __name__ == '__main__':
    main()


