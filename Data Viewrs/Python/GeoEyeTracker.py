

import cv2
#from matplotlib import cm
import math
import numpy as np

from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt

from Plane_projector import Plane_projector
from GeoEyeEngine import GeoEyeEngine




class GeoEyeTracker(QMainWindow):
   Showfinished = pyqtSignal() 
   EyePts = pyqtSignal(float) 
   GazePositionRight = pyqtSignal(np.ndarray) 
   GazePositionLeft = pyqtSignal(np.ndarray) 


   def __init__(self):
       super().__init__()
       # initialize the opencv


       self.videos = []

       self.currentVideoInd = 0
       self.CurrMaxFrame = 0 



       a = 1
       b = 1
       self.kernel = np.zeros((2*b+1, 2*a+1))
       y,x = np.ogrid[-b:b+1, -a:a+1]
       mask = x**2/a**2 + y**2/b**2 <= 1
       self.kernel[mask] = 1/(np.pi*a*b)
       self.kernel = np.array([[0,0,0],[0,3,0],[0,0,0]])
       #Kernelsize = 3
       #self.kernel = np.ones((Kernelsize,Kernelsize),np.float32)/(Kernelsize*Kernelsize)

       print(self.kernel)
    
       contribute = 0.5;
       self.PPRight = Plane_projector('Right')
       self.PPLeft = Plane_projector('Left')
       
       self.GeoEngR = GeoEyeEngine('Right')  
       self.GeoEngL = GeoEyeEngine('Left')  

       
       self.countImgR = np.zeros((256,512))
       self.countImgL = np.zeros((256,512))

       self.RefDispPoints = np.float32([[0,0], [0,0], [0,0], [0,0]])

       self.numCalTars = 1
       #self.result = cv2.VideoWriter('eye.avi',
       #                  cv2.VideoWriter_fourcc(*'XVID'),
       #                  25, (1024, 256), isColor= False)

       self.SyncEnabled = False
       self.eyeTSArray  = np.array([0])

       self.EyeFrameCount = 0

   def showFrame(self):
       
       ret, frame = self.cap.read()
       self.EyeFrame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)

       if self.EyeFrame >= self.CurrMaxFrame or ret == False: 
           if self.currentVideoInd < len(self.videos)-1:    
               self.NextVideo()
               return
           else: 
               self.Showfinished.emit()
               return

       pts = self.cap.get(cv2.CAP_PROP_POS_MSEC)

       #print('Eye PTS:', pts)
       if self.SyncEnabled:
           self.EyePts.emit(self.eyeTSArray[self.EyeFrameCount])
       else:
           self.EyePts.emit(pts)
       self.EyeFrameCount += 1
       
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
       gray = cv2.filter2D(gray,-1,self.kernel,borderType=cv2.BORDER_CONSTANT)
       


       ImgR1 = gray[:,:256]
       ImgR2 = gray[:,256:512]
       ImgL1 = gray[:,512:768]
       ImgL2 = gray[:,768:1024]
         
       # First image of right eye
       self.PPRight.TrackPupils(ImgR1, ImgR2, self.countImgR, self.EyeFrame, self.GeoEngR, self.RefDispPoints)
       self.PPLeft.TrackPupils(ImgL1, ImgL2, self.countImgL, self.EyeFrame, self.GeoEngL, self.RefDispPoints)

       outImg = cv2.hconcat([self.PPRight.ImInter1, self.PPRight.ImInter2, self.PPLeft.ImInter1, self.PPLeft.ImInter2])
       self.countImg = cv2.hconcat([self.countImgR, self.countImgL])

       self.GazePositionRight.emit(self.GeoEngR.InterSolver.GazeVout)
       self.GazePositionLeft.emit(self.GeoEngL.InterSolver.GazeVout)

       if ret == True:
           #cv2.imshow('R1',ImgR1)
           cv2.imshow('Orig',outImg)
           cv2.imshow('Counto',self.countImg)

           #self.result.write(outImg)

       #if self.EyeFrame >= 1600:
       #    print('SaveBitch')
       #   self.result.release()
       #    self.Showfinished.emit()

   def CalibrateEyePos(self):
       print('Claculating '+str(self.numCalTars) +'th position')
       self.PPRight.ShowGeoContAve(self.EyeFrame,10, self.numCalTars )
       self.PPLeft.ShowGeoContAve(self.EyeFrame,10, self.numCalTars )
       self.numCalTars += 1

   def SaveCalibration(self):
       self.GeoEngR.SaveRPStructures()
       self.GeoEngL.SaveRPStructures()

   def LoadCalibration(self):
       self.GeoEngR.LoadRPStructures()
       self.GeoEngL.LoadRPStructures()


   def ResetKs(self):
       self.GeoEngR.ResetKs()
       self.GeoEngL.ResetKs()

   def EndShow(self):
       self.cap.release()
       # Closes all the frames
       cv2.destroyAllWindows()


   def NextVideo(self):    
       self.cap.release()
       self.currentVideoInd += 1 
       self.VideoCapSetup()

   def VideoCapSetup(self):

       self.cap = cv2.VideoCapture(self.videos[self.currentVideoInd])

       if (self.cap.isOpened()== False):
           print("Error opening video stream or file")

       self.CurrMaxFrame = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
       print("Toral Frames: ", self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

   def SetVideoFiles(self, VideoList):
       self.videos = VideoList
       print(VideoList)
       self.VideoCapSetup()
       self.cap.set(cv2.CAP_PROP_POS_FRAMES, 800)

   def EnableSynch(self, state):
       if state == Qt.Checked:
           self.SyncEnabled = True
           print('Synching enabled')
       else:
           self.SyncEnabled = False
           print('Synching disabled')

   @pyqtSlot(np.ndarray)
   def UpdateTSeye(self, TSs):
       self.eyeTSArray = TSs


   @pyqtSlot(np.ndarray)   
   def UpdateDisplayEdges(self, edgePoints):

       self.RefDispPoints = edgePoints
       #print("points", edgePoints)
