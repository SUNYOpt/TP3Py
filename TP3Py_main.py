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
import importlib.util

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
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow, QListWidget, QCheckBox
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt
from functools import partial
from datetime import datetime
#from TobiiExtract import TobiiExtract
from TP3py_Gstream import TP3py_Gstream

from pathlib import Path

from pynput import keyboard
import websocket

# root = "./"
# ModuleDir = './Modules/'


# Im looking into importing modules here
class ModuleHandler():
   def __init__(self):
        super().__init__()    
        
        # Array containing all classes of modules
        self.ModArray = []
        self.OpenMods = []

   #TODO check if module exists & check if module is compatible
   def check_module(self, f):
       return True
   
    
   def add_modules(self, files):
       oks = []
       count = 0
       for f in files:
           if self.check_module(f):
               self.ModArray.append(os.path.normpath(f))
               oks.append(count)
               count += 1
       return oks       
               
   def rem_modules(self, files):
       for f in files:
           self.ModArray.remove(f)

   """
   def ModuleInit(self, Mod_names):
        global ModuleDir 
        moduleList = glob.glob(ModuleDir+"*.py") 
        path = Path(__file__).parent.absolute()

        # First priority would be the module directory
        sys.path.insert(0,os.path.join(path, ModuleDir))

        # Importing all selected modules
        for currName in moduleList:
            print (currName[len(ModuleDir):-3])
            module  = __import__(currName[len(ModuleDir):-3])

            cls = getattr(module, currName[len(ModuleDir):-3])
            print(currName[len(ModuleDir):-3])
            
            #Initializing mods
            self.OpenMods.append(cls())
            
            # Current module's thread
            cModuleThread = QThread()
            # Array of all threads
            self.OpenModsThreads.append(cModuleThread)
            
            # Initializing modules
            module = cls(gstreamWorker)
            module.moveToThread(self.OpenModsThreads[self.moduleCounter])

            self.OpenModsThreads[self.moduleCounter].start()

            self.moduleCounter += 1
   """

   # __import__('D:\\GitHub\\TP3Py\\Modules\\RandomPlot')
   #TODO
   def start_all(self, gstreamWorker):
       self.close_all()
       for m in self.ModArray:
            sys.path.append(os.path.join(*os.path.split(m)[:-1]))
            # spec = importlib.util.spec_from_file_location(m, __file__)
            # module = importlib.util.module_from_spec(spec)
            module  = __import__(os.path.split(m)[-1][:-3])
            cls = getattr(module, os.path.split(m[:-3])[-1])
            self.OpenMods.append(cls(gstreamWorker))
            
            
   def rem_modules_by_index(self, i):
       del self.ModArray[i]

   def close_all(self):
       for m in self.OpenMods:
           m.close()
       del self.OpenMods[:]
       
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


        self.CalibStatus = False
        # Set some main window's properties
        self.setWindowTitle('Tobii 3 Recorder')
        #self.setFixedSize(1200, 600)
        # Set the central widget
        self._centralWidget = QWidget(self)
        self.generalLayout =  QGridLayout()
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        
        self.startbutton  = QPushButton('Start Experiment')
        self.Calibbutton  = QPushButton('Eye Calibration')
        self.endbutton    = QPushButton('End Experiment')
        self.addmodule    = QPushButton('Add Module(s)')
        self.removemodule = QPushButton('Remove Module(s)')
        self.openmodules  = QPushButton('Open')


        self.listwidget = QListWidget()
        self.CalCheckbox = QCheckBox(':Calibrated')


        self.generalLayout.addWidget(QLabel('<h2>Initials:</h2>'), 0, 0)
        self.InitialEntry = QLineEdit()
        self.generalLayout.addWidget(self.InitialEntry, 0, 1)
        self.generalLayout.addWidget(self.startbutton, 2, 0)
        self.generalLayout.addWidget(self.Calibbutton, 3, 0)
        self.generalLayout.addWidget(self.CalCheckbox, 3, 1)

        self.generalLayout.addWidget(self.endbutton, 2, 2)

        self.generalLayout.addWidget(QLabel('<h3>Experiment Name:</h3>'), 1, 0)
        self.ExpNameEntry = QLineEdit()
        self.generalLayout.addWidget(self.ExpNameEntry, 1, 1)
        self.generalLayout.addWidget(self.addmodule   , 3, 3)
        self.generalLayout.addWidget(self.removemodule, 3, 4)

        self.generalLayout.addWidget(self.listwidget, 2, 3, 1, 3)



        self.InitialEntry.textChanged.connect(self.InitialEcho)
        self.ExpNameEntry.textChanged.connect(self.ExpNameEcho)
        

        # Start Button action:
        self.startbutton.clicked.connect(self.InitializeGstreamer)

        # AddModule Button action:
        self.addmodule.clicked.connect(self.addmodulefun)
        
        # RemoveModule Button action:
        self.removemodule.clicked.connect(self.remmodulefun)
        
        # openModule Button action:
        self.startbutton.clicked.connect(self.openmodulefun)

        # Initializing Eye Calibration
        self.Calibbutton.clicked.connect(self.EyeCalibrateOverWebS)

        # List of modules to be selected in the pipline 
        self.listwidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listwidget.itemClicked.connect(self.printItemText)
        # # selected items
        # for item in self.listwidget.selectedItems():
        #     print(item.text())
        #self.setKeyIncoming()
        #self.pausebutton.setCheckable(True)
        self.startbutton.clicked.connect(self.setKeyIncoming)
        self.endbutton.clicked.connect(self.setKeyOFF)

        # A class for handling the modules
        self.ModuleHandler = ModuleHandler()

   def InitializeGstreamer(self):
       # Here we define the Gstreamer thread
       self.thread = QThread()
       GstreamWorker = TP3py_Gstream()

       # Module Handler Thread loads the modules
       # To do: not a thread currently
       #self.ModuleHandler = ModuleHandler()

       # connect stop signal to worker stop method
       self.stop_signal.connect(GstreamWorker.stop)
       GstreamWorker.moveToThread(self.thread)

       # connect the workers finished signal to stop gstreamer thread
       GstreamWorker.Gstreamfinished.connect(self.thread.quit)
       # connect the workers finished signal to clean up worker
       GstreamWorker.Gstreamfinished.connect(GstreamWorker.deleteLater)
       # connect threads finished signal to clean up thread
       self.thread.finished.connect(self.thread.deleteLater)

       self.thread.started.connect(GstreamWorker.do_work)
       # self.thread.finished.connect(GstreamWorker.stop)

       # Start Button action:
       self.thread.start()

       # Stop Button action:
       self.endbutton.clicked.connect(self.stop_thread)

       self.thread.GstreamWorker = GstreamWorker
       self.thread.GstreamWorker.setInitName(self.InitialEntry.text())
       self.thread.GstreamWorker.setExpName(self.ExpNameEntry.text())

   def on_KeyPress(self, key):
       print(key)

       self.thread.GstreamWorker.EstablishKeyworkEvents(key)

   def setKeyIncoming(self):
       # Start a keyboard listener for entering events with keys
       # Keyboard Listener
       self.listener = keyboard.Listener(on_press=self.on_KeyPress)
       self.listener.start()

   def setKeyOFF(self):
       #self.listener = keyboard.Listener(on_press=None)
       self.listener.stop()
   # When stop_btn is clicked this runs. Terminates the worker and the thread.
   def stop_thread(self):
       self.stop_signal.emit()  # emit the finished signal on stop

       self.CalibStatus = False
       self.CalCheckbox.setChecked(False)
       self.CalCheckbox.setStyleSheet("QCheckBox::indicator"
                                  "{"
                                  "background-color : red;"
                                  "}")

   # When browse_btn is clicked this runs. 
   def addmodulefun(self):
       self.openFileNamesDialog()
        
   # When browse_btn is clicked this runs. 
   def remmodulefun(self):
        modules_indices = []
        for i in self.listwidget.selectedIndexes():
            modules_indices.append(i.row())
            ind = self.listwidget.takeItem(i.row())
        for i in modules_indices[::-1]:
            self.ModuleHandler.rem_modules_by_index(i) 
        
        
   def openmodulefun(self):
        self.ModuleHandler.start_all(self.thread.GstreamWorker)
        
        
   def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"Select Modules to Add", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            oks = self.ModuleHandler.add_modules(files)
            
            for i in range(len(oks)):
                # add some items
                it = QtWidgets.QListWidgetItem(os.path.split(files[oks[i]])[-1][:-3])
                self.listwidget.addItem(it)
                # it.setSelected(True)
            
        
   def InitialEcho(self):
        print("Initials: "+ self.InitialEntry.text())
        namestring = self.InitialEntry.text()

   def ExpNameEcho(self):
        print("Exp. Name: "+ self.ExpNameEntry.text())
        namestring = self.ExpNameEntry.text()

   def EyeCalibrateOverWebS (self):

        # Establishing connection with web socket server for doing calibration
        ws = websocket.create_connection("ws://192.168.75.51/websocket",  subprotocols=["g3api", "base64"])
        #To recieve the position of the calibration marker: Message = {"path":"calibrate!emit-markers", "id":21, "method":"POST", "body": []}
        # Calling calibration action
        Message = {"path":"calibrate!run", "id":23, "method":"POST", "body": []}
        ws.send(json.dumps(Message))
        result = ws.recv()
        print("Received '%s'" % result)
        jsonMess = json.loads(result)
        ws.close()

        if jsonMess['body'] == True:
            self.CalibStatus = True
            self.CalCheckbox.setChecked(True)
            self.CalCheckbox.setStyleSheet("QCheckBox::indicator"
                                   "{"
                                   "background-color : lightgreen;"
                                   "}")

        if jsonMess['body'] == False:
            self.CalibStatus = False
            self.CalCheckbox.setChecked(False)
            self.CalCheckbox.setStyleSheet("QCheckBox::indicator"
                                   "{"
                                   "background-color : red;"
                                   "}")
   def printItemText(self):       
        items = self.listwidget.selectedItems()
        x = []
        for i in range(len(items)):
            x.append(str(self.listwidget.selectedItems()[i].text()))

        #print (x)
        # self.ModuleHandler.ModuleInit(x)

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


