import cv2
#from matplotlib import cm
import math
import numpy as np
import scipy.io

from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

import matplotlib.pyplot as plt
import json
from collections import namedtuple


class SyncAgent(QMainWindow):
   Showfinished = pyqtSignal()
   sceneTSS = pyqtSignal(np.ndarray)
   eyeTSS = pyqtSignal(np.ndarray)

   def __init__(self):
       super().__init__()
       # initialize the opencv
       self.IMUFile = []
       self.GazeFile = []
       self.TSFile = []
       self.BDFile = []

       self.ttlTimeArray =[]

       self.TrigPos = 1

       
   def setRawFiles(self, IMUFile, GazeFile, TSFile, BDFile):
       self.IMUFile = IMUFile
       self.GazeFile = GazeFile
       self.TSFile = TSFile
       self.BDFile = BDFile

       print(IMUFile)

   def ShowRawData(self):

       self.TimeArray, self.Gaze2DxArray, self.Gaze2DyArray, self.LeftPupil, self.RightPupil, self.TimeLeftE, self.TimeRightE= self.GetGazeData()
       # ----- ISSUE WITH DATA
       AccTimeArray, AccxArray, AccyArray, AcczArray, GyroxArray, GyroyArray, GyrozArray, MagTimeArray, MagxArray, MagyArray, MagzArray = self.GetIMUData()

       sceneMSTSArray, eyeMSTSArray, ttseyeArray, ttssceneArray, self.ttlTimeArray = self.GetTSData()
       print('sceneTSnumel', len(ttssceneArray))
       print('eyeTSnumel', len(ttseyeArray))

       self.sceneTSS.emit(ttssceneArray)
       self.eyeTSS.emit(ttseyeArray)



       # Find corresponding timestamps of the Videos and check later their frame number
       for sceneMTS in sceneMSTSArray:
           print(sceneMTS)
           ind = np.where(abs(ttssceneArray-sceneMTS) == min(abs(ttssceneArray-sceneMTS)))
           print(ind)

       # Find corresponding timestamps of the Videos and check later their frame number
       for eyeMTS in eyeMSTSArray:
           print(eyeMTS)
           ind = np.where(abs(ttseyeArray-eyeMTS) == min(abs(ttseyeArray-eyeMTS)))
           print(ind)

       plt.rcParams.update({'font.size': 12, 'lines.linewidth': 2})
       fig = plt.figure()
       ax = fig.add_axes((0.05, 0.55, 0.4, 0.4))
       ax.plot(self.TimeArray, self.Gaze2DxArray, 'b')
       ax.plot(self.TimeArray, self.Gaze2DyArray, 'r')
       ax.plot(self.ttlTimeArray, np.ones(len(self.ttlTimeArray)), 'r.')
       plt.title(label="Gaze 2D-- Tobii's")

       ax.spines["top"].set_visible(False)
       ax.spines["right"].set_visible(False)
       ax.spines["bottom"].set_linewidth(2)
       ax.spines["left"].set_linewidth(2)
       ax.xaxis.set_tick_params(width=2)
       ax.yaxis.set_tick_params(width=2)

       # Plot pupils
       ax = fig.add_axes((0.05, 0.05, 0.4, 0.4))
       ax.plot(self.TimeLeftE, self.LeftPupil, 'b')
       ax.plot(self.TimeRightE, self.RightPupil, 'r')
       ax.plot(self.ttlTimeArray, np.ones(len(self.ttlTimeArray)), 'r.')
       #ax.plot(ttssceneArray, 1.1*np.ones(len(ttssceneArray)), 'b.')
       plt.title(label="Pupil diameter (mm)")
       ax.spines["top"].set_visible(False)
       ax.spines["right"].set_visible(False)
       ax.spines["bottom"].set_linewidth(2)
       ax.spines["left"].set_linewidth(2)
       ax.xaxis.set_tick_params(width=2)
       ax.yaxis.set_tick_params(width=2)

       # IMU pupils
       ax = fig.add_axes((0.55, 0.75, 0.4, 0.18))
       ax.plot(AccTimeArray, AccxArray, 'b')
       ax.plot(AccTimeArray, AccyArray, 'r')
       ax.plot(AccTimeArray, AcczArray, 'g')

       ax.plot(self.ttlTimeArray, np.ones(len(self.ttlTimeArray)), 'r.')
       #ax.plot(ttssceneArray, 1.1*np.ones(len(ttssceneArray)), 'b.')
       plt.title(label="Accelerometer")
       ax.spines["top"].set_visible(False)
       ax.spines["right"].set_visible(False)
       ax.spines["bottom"].set_linewidth(2)
       ax.spines["left"].set_linewidth(2)
       ax.xaxis.set_tick_params(width=2)
       ax.yaxis.set_tick_params(width=2)

       ax = fig.add_axes((0.55, 0.5, 0.4, 0.18))
       ax.plot(AccTimeArray, GyroxArray, 'b')
       ax.plot(AccTimeArray, GyroyArray, 'r')
       ax.plot(AccTimeArray, GyrozArray, 'g')

       ax.plot(self.ttlTimeArray, np.ones(len(self.ttlTimeArray)), 'r.')
       #ax.plot(ttssceneArray, 1.1*np.ones(len(ttssceneArray)), 'b.')
       plt.title(label="Gyroscope")
       ax.spines["top"].set_visible(False)
       ax.spines["right"].set_visible(False)
       ax.spines["bottom"].set_linewidth(2)
       ax.spines["left"].set_linewidth(2)
       ax.xaxis.set_tick_params(width=2)
       ax.yaxis.set_tick_params(width=2)

       ax = fig.add_axes((0.55, 0.25, 0.4, 0.18))
       ax.plot(MagTimeArray, MagxArray, 'b')
       ax.plot(MagTimeArray, MagyArray, 'r')
       ax.plot(MagTimeArray, MagzArray, 'g')

       ax.plot(self.ttlTimeArray, np.ones(len(self.ttlTimeArray)), 'r.')
       #ax.plot(ttssceneArray, 1.1*np.ones(len(ttssceneArray)), 'b.')
       plt.title(label="Magnetometer")
       ax.spines["top"].set_visible(False)
       ax.spines["right"].set_visible(False)
       ax.spines["bottom"].set_linewidth(2)
       ax.spines["left"].set_linewidth(2)
       ax.xaxis.set_tick_params(width=2)
       ax.yaxis.set_tick_params(width=2)
       plt.show()

   def ShowOnsetData(self):

       timeonset = self.ttlTimeArray[self.TrigPos]
       timeoffset =self.ttlTimeArray[self.TrigPos+1]

       oiT = np.where(np.logical_and(self.TimeArray >  timeonset, self.TimeArray < timeoffset))
       oiT = np.squeeze(oiT)

       oiTLPup = np.where(np.logical_and(self.TimeLeftE >  timeonset, self.TimeLeftE < timeoffset))
       oiTRPup = np.where(np.logical_and(self.TimeRightE >  timeonset, self.TimeRightE < timeoffset))
       oiTLPup = np.squeeze(oiTLPup)
       oiTRPup = np.squeeze(oiTRPup)

       print(oiT)
       fig = plt.figure()
       ax = fig.add_axes((0.05, 0.55, 0.4, 0.4))
       ax.plot(self.TimeArray[oiT], self.Gaze2DxArray[oiT], 'b')
       ax.plot(self.TimeArray[oiT], self.Gaze2DyArray[oiT], 'r')
       plt.title(label="Gaze 2D-- Tobii's")

       ax.spines["top"].set_visible(False)
       ax.spines["right"].set_visible(False)
       ax.spines["bottom"].set_linewidth(2)
       ax.spines["left"].set_linewidth(2)
       ax.xaxis.set_tick_params(width=2)
       ax.yaxis.set_tick_params(width=2)


       # Plot pupils
       ax = fig.add_axes((0.05, 0.05, 0.4, 0.4))
       ax.plot(self.TimeLeftE[oiTLPup], self.LeftPupil[oiTLPup], 'b')
       ax.plot(self.TimeRightE[oiTRPup], self.RightPupil[oiTRPup], 'r')
       #ax.plot(ttssceneArray, 1.1*np.ones(len(ttssceneArray)), 'b.')
       plt.title(label="Pupil diameter (mm)")
       ax.spines["top"].set_visible(False)
       ax.spines["right"].set_visible(False)
       ax.spines["bottom"].set_linewidth(2)
       ax.spines["left"].set_linewidth(2)
       ax.xaxis.set_tick_params(width=2)
       ax.yaxis.set_tick_params(width=2)


       plt.show()
       self.TrigPos += 1

   def GetGazeData(self):
       TimeArray = []
       Gaze2DxArray = []
       Gaze2DyArray = []

       LeftPupil = []
       TimeLeftE = []
       RightPupil = []
       TimeRightE = []

       # There is only one file for gaze, etc.
       with open(self.GazeFile[0]) as f:
           lines = (f.readlines())

       for streamString in lines:
           #print('st:', streamString[0:len(streamString)])

           GazeD = json.loads(streamString[0:len(streamString)], object_hook=
           lambda d: namedtuple('X', d.keys())
           (*d.values()))

           TimeArray.append(GazeD.tgz)
           Gaze2DxArray.append(GazeD.gaze2d[0])
           Gaze2DyArray.append(GazeD.gaze2d[1])
           #print(GazeD)
           if hasattr(GazeD.eyeleft,'pupildiameter'):
               LeftPupil.append(GazeD.eyeleft.pupildiameter)
               TimeLeftE.append(GazeD.tgz)
           if hasattr(GazeD.eyeright,'pupildiameter'):
               RightPupil.append(GazeD.eyeright.pupildiameter)
               TimeRightE.append(GazeD.tgz)
       return np.array(TimeArray), np.array(Gaze2DxArray), np.array(Gaze2DyArray), np.array(LeftPupil), np.array(RightPupil), np.array(TimeLeftE), np.array(TimeRightE)

   def GetIMUData(self):
       AccTimeArray = []
       AccxArray = []
       AccyArray = []
       AcczArray = []
       GyroxArray = []
       GyroyArray = []
       GyrozArray = []

       MagTimeArray = []
       MagxArray = []
       MagyArray = []
       MagzArray = []
       # There is only one file for gaze, etc.
       with open(self.IMUFile[0]) as f:
           lines = (f.readlines())

       for streamString in lines:
           #print('st:', streamString[0:len(streamString)])

           IMUD = json.loads(streamString[0:len(streamString)], object_hook=
           lambda d: namedtuple('X', d.keys())
           (*d.values()))

           if hasattr(IMUD,'tacc'):
               AccTimeArray.append(IMUD.tacc)
               AccxArray.append(IMUD.accelerometer[0])
               AccyArray.append(IMUD.accelerometer[1])
               AcczArray.append(IMUD.accelerometer[2])

               GyroxArray.append(IMUD.gyroscope[0])
               GyroyArray.append(IMUD.gyroscope[1])
               GyrozArray.append(IMUD.gyroscope[2])

           if hasattr(IMUD,'tmag'):
               MagTimeArray.append(IMUD.tmag)
               MagxArray.append(IMUD.magnetometer[0])
               MagyArray.append(IMUD.magnetometer[1])
               MagzArray.append(IMUD.magnetometer[2])

       return AccTimeArray, AccxArray, AccyArray, AcczArray, GyroxArray, GyroyArray, GyrozArray, MagTimeArray, MagxArray, MagyArray, MagzArray

   def GetTSData(self):
       sceneMSTSArray = []
       eyeMSTSArray = []
       ttseyeArray = []
       ttssceneArray = []
       ttlTimeArray = []
       # There is only one file for gaze, etc.
       with open(self.TSFile[0]) as f:
           lines = (f.readlines())

       for streamString in lines:
           #print('st:', streamString[0:len(streamString)])

           TSD = json.loads(streamString[0:len(streamString)], object_hook=
           lambda d: namedtuple('X', d.keys())
           (*d.values()))

           if hasattr(TSD,'sceneMSTS'):
               sceneMSTSArray.append(TSD.sceneMSTS)
           if hasattr(TSD,'eyeMSTS'):
               eyeMSTSArray.append(TSD.eyeMSTS)
           if hasattr(TSD, 'ttseye'):
               ttseyeArray.append(TSD.ttseye)
           if hasattr(TSD, 'ttsscene'):
               ttssceneArray.append(TSD.ttsscene)
           if hasattr(TSD, 'tttl'):
               if TSD.value == 1:
                   ttlTimeArray.append(TSD.tttl)

       return np.array(sceneMSTSArray), np.array(eyeMSTSArray), np.array(ttseyeArray), np.array(ttssceneArray), np.array(ttlTimeArray)