

import cv2
#from matplotlib import cm
import math
import numpy as np


from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton, QCheckBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

from PyQt5.QtCore import QTimer,QDateTime

from SceneToHeadCoords import SceneToHeadCoords
from GeoEyeTracker import GeoEyeTracker
from SyncAgent import SyncAgent

import sys
import os

class TobiiRecUI(QMainWindow):
   global ModuleDir

   stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread

   def __init__(self):
        super().__init__()

        self.IMUdataFN = []
        self.SceneFN =[]
        self.EyeFN = []
        self.GazedataFN = []
        self.TSdataFN= []
        self.BData = []

        # Set some main window's properties
        self.setWindowTitle('Semimetric offline tracker')
        #self.setFixedSize(1200, 600)
        # Set the central widget
        self._centralWidget = QWidget(self)
        self.generalLayout =  QGridLayout()
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self.OpenFolder = QPushButton('Open folder')
        self.generalLayout.addWidget(self.OpenFolder, 1, 0)

        self.startbutton = QPushButton('start experiment')
        self.generalLayout.addWidget(self.startbutton, 2, 0)
              
        self.SaveCalib = QPushButton('Save Calib')
        self.generalLayout.addWidget(self.SaveCalib, 3, 0)

        self.LoadCalib = QPushButton('load Calib')
        self.generalLayout.addWidget(self.LoadCalib, 4, 0)

        self.ShowRawData = QPushButton('Show IMU/Gaze raw data')
        self.generalLayout.addWidget(self.ShowRawData, 1, 1)

        self.AddTarget = QPushButton('Add Calib Target')
        self.generalLayout.addWidget(self.AddTarget, 2, 2)


        self.NextTTL = QPushButton('Next Trigger')
        self.generalLayout.addWidget(self.NextTTL, 3, 1)
        
        self.TScb = QCheckBox('Sync with TS data')
        self.generalLayout.addWidget(self.TScb , 2, 1)

        self.ScenePosbutton = QPushButton('Get Scene-based pos')
        self.generalLayout.addWidget(self.ScenePosbutton, 1, 3)

        self.Scnethread = QThread()
        self.Eyethread = QThread()
        self.Syncthread = QThread()
        
        
        self.timer=QTimer(self)
        self.timer.setInterval(20)

        SceneWorker = SceneToHeadCoords()
        Eyeworker = GeoEyeTracker()
        SyncWorker = SyncAgent()
        
        
        SceneWorker.moveToThread(self.Scnethread)
        Eyeworker.moveToThread(self.Eyethread)
        SyncWorker.moveToThread(self.Syncthread)

        # Cleaning up once the communication ends
        SceneWorker.Showfinished.connect(self.Scnethread.quit) 
        SceneWorker.Showfinished.connect(SceneWorker.deleteLater)  
        self.Scnethread.finished.connect(self.Scnethread.deleteLater)

        # Updating the TS vectors of eye and scene workers
        SyncWorker.eyeTSS.connect(Eyeworker.UpdateTSeye)
        SyncWorker.sceneTSS.connect(SceneWorker.UpdateTSscene)
        
        Eyeworker.EyePts.connect(SceneWorker.UpdateEyePts) 
        Eyeworker.GazePositionRight.connect(SceneWorker.UpdateGazePositionRight) 
        Eyeworker.GazePositionLeft.connect(SceneWorker.UpdateGazePositionLeft) 

        SceneWorker.DisplayEdges.connect(Eyeworker.UpdateDisplayEdges) 
        


        Eyeworker.Showfinished.connect(self.Eyethread.quit) 
        Eyeworker.Showfinished.connect(Eyeworker.deleteLater)  
        self.Scnethread.finished.connect(self.Eyethread.deleteLater) 
        self.Scnethread.finished.connect(SceneWorker.EndShow)
        self.Eyethread.finished.connect(Eyeworker.EndShow)
        self.timer.timeout.connect(SceneWorker.showFrame)
        self.timer.timeout.connect(Eyeworker.showFrame)

        # Starting the operations either with timer or other analysis
        self.startbutton.clicked.connect(self.timer.start)
        self.ScenePosbutton.clicked.connect(SceneWorker.ProcessSceneFrame4Pos)

        self.AddTarget.clicked.connect(Eyeworker.CalibrateEyePos)

        self.SaveCalib.clicked.connect(Eyeworker.SaveCalibration)
        self.LoadCalib.clicked.connect(Eyeworker.LoadCalibration)
        self.OpenFolder.clicked.connect(self.openFileNamesDialog)
        self.cb.stateChanged.connect(SceneWorker.EnableET)

        self.TScb.stateChanged.connect(SceneWorker.EnableSynch)
        self.TScb.stateChanged.connect(Eyeworker.EnableSynch)

        self.ShowRawData.clicked.connect(SyncWorker.ShowRawData)
        self.NextTTL.clicked.connect(SyncWorker.ShowOnsetData)

        self.Scnethread.SceneWorker = SceneWorker
        self.Eyethread.Eyeworker = Eyeworker
        self.Syncthread.SyncWorker = SyncWorker


   def openFileNamesDialog(self):
        home = os.getenv("HOME")

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        data_dir = QFileDialog.getExistingDirectory(self, "Select data folder", home,
                                                options=options)

        if data_dir:
             file_list = os.listdir(data_dir)
             print(file_list)
             file_list.sort()
             print(file_list)

             for file in file_list:
                  print(file)
                  self.ClassifyFiles(file, data_dir)

             self.Eyethread.Eyeworker.SetVideoFiles(self.EyeFN)
             self.Scnethread.SceneWorker.SetVideoFiles(self.SceneFN)
             self.Syncthread.SyncWorker.setRawFiles(self.IMUdataFN,self.GazedataFN, self.TSdataFN,  self.BData)

   def ClassifyFiles(self, filename, data_dir):
        Idash = filename.find('-') # Find the lowest index of '-'
        Tag = filename[0:Idash]

        Gfilename = os.path.join(data_dir, filename)
        if Tag == 'IMUdata':
            self.IMUdataFN.append(Gfilename)
        elif Tag == 'scene':
            self.SceneFN.append(Gfilename)
        elif Tag == 'eye':
            self.EyeFN.append(Gfilename)
        elif Tag == 'Gazedata':
            self.GazedataFN.append(Gfilename)
        elif Tag == 'TSdata':
            self.TSdataFN.append(Gfilename)
        elif Tag == 'BD':    # Behavioral .mat file
            self.BData.append(Gfilename)
           
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

