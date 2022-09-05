
import cv2
#from matplotlib import cm
import math
import numpy as np
import json

from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt

class SceneToHeadCoords(QMainWindow):
   Showfinished = pyqtSignal() 
   DisplayEdges = pyqtSignal(np.ndarray) 


   def __init__(self):
       super().__init__()
       # initialize the opencv
       self.videos = []
      
       f = open('Cal.json')
       Calibdata = json.loads(json.load(f))
       f.close()

       self.mtx = np.array(Calibdata['mtx'])
       self.dist =  np.array(Calibdata['dist'])
       #self.dist = np.array([self.dist[0,0],  self.dist[0,1],0, 0, 0])
       print('Mtx:', self.mtx)       
       print('Mtx:', self.dist)

       self.currentVideoInd = 0



       self.Threshold = 150
       self.DisplayL = 65
       self.DisplayW = 45
       self.Cameraf= 500
       self.GlobalDisplayCoords = np.array([[self.DisplayL/2, -self.DisplayW/2, 0], [-self.DisplayL/2, -self.DisplayW/2, 0], [-self.DisplayL/2, self.DisplayW/2, 0], [self.DisplayL/2, self.DisplayW/2, 0]], np.float32)
       #CameraIntrinM = np.array([[Cameraf, 0, 0],[0, Cameraf, 0],[0, 0, 1]], np.float32)
       #DistortionCoeffs = np.zeros((1,4))
       self.axis = np.float32([[0,0,0], [30,0,0], [0,30,0], [0,0,-30]]).reshape(-1,3)
        
       self.SmoothDispPos = np.float32([[0,0], [0,0], [0,0], [0,0]])
       self.SmoothTarPos = np.float32([0,0])

       self.SmoothRefPos = np.float32([[0,0], [0,0], [0,0], [0,0], [0,0]])

       self.MovingDispContrib = 0.1
       
       self.GazePosRight = np.float32([1, 1])
       self.GazePosLeft = np.float32([1, 1])


       #self.result = cv2.VideoWriter('Scene2.avi',
       #                  cv2.VideoWriter_fourcc(*'XVID'),
       #                  12, (960, 540), isColor= False)

       self.filewriter = open('ETdata-' + ".txt", 'w')

       self.EyeTrackEnabled = False
       self.SyncEnabled = False
       self.sceneTSArray  = np.array([0])

       self.SceneFrameCount = 0

   # Presenting the scene with timely matter
   def showFrame(self):
       
       framnum = self.EyePts//30
       #self.cap.set(cv2.CAP_PROP_POS_MSEC, self.EyePts)
       #self.cap.set(cv2.CAP_PROP_POS_FRAMES, framnum)

       if self.SyncEnabled:
           Scenepts = self.sceneTSArray[self.SceneFrameCount]
       else:
           Scenepts = self.cap.get(cv2.CAP_PROP_POS_MSEC)

       contoursFrame =  np.zeros((540, 960), dtype=np.uint8)

       # Wait until a eye video timestamp becomes available
       if self.EyePts < Scenepts :
           #print("ret", Scenepts)
           return

       ret, frame = self.cap.read()
       SceneFrame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
       self.SceneFrameCount += 1
       
       if SceneFrame >= self.CurrMaxFrame or ret == False: 
           print('Next Video')          
           if self.currentVideoInd < len(self.videos)-1:    
               self.NextVideo()
               return
           else: 
               self.Showfinished.emit()
               return

       #print(frame.shape)
       #print('Scene PTS:', Scenepts)

       resizdFrame = cv2.resize(frame, (960, 540))

       gray = cv2.cvtColor(resizdFrame, cv2.COLOR_BGR2GRAY)

       h, w = gray.shape[:2]
       newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (w, h), 1, (w, h))
       gray = cv2.undistort(gray, self.mtx, self.dist, None, newcameramtx)

       # gray= cv2.GaussianBlur(gray, (25,25), 0)
       edges = cv2.Canny(gray, 100, 200, 3, L2gradient=True)

       cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

       for cnt in cnts:
           # Perimeter of the closed contours
           perimeter = cv2.arcLength(cnt, True)

           if (perimeter) < 200 or (perimeter) > 3000:
               continue
           # contoursFrame = cv2.drawContours(contoursFrame, [cnt], 0, (255, 0, 255), 1)

           epsilon = 0.05 * perimeter
           approx = cv2.approxPolyDP(cnt, epsilon, True)

           area = cv2.contourArea(cnt)
           areaPeriRatio = area / perimeter
           if approx.shape[0] == 4 and areaPeriRatio > 10:
               # print(area/perimeter)
               contoursFrame = cv2.drawContours(contoursFrame, [approx], 0, (255, 0, 255), 1)
               # for p in range(approx.shape[0]):
               # gray = cv2.circle(gray, (approx[p,0,0],approx[p,0,1]), radius=10, color=(255, 0, 255), thickness=-1
               self.UpdateDispPos(approx)

               area = cv2.contourArea(cnt)
               areaPeriRatio = area / perimeter

               print(area / perimeter)
               contoursFrame = cv2.drawContours(contoursFrame, [approx], 0, (255, 0, 255), 1)
               for p in range(self.SmoothDispPos.shape[0]):
                   gray = cv2.circle(gray,
                                     (self.SmoothDispPos[p, 0].astype(np.int), self.SmoothDispPos[p, 1].astype(np.int)),
                                     radius=10, color=(255, 0, 255),
                                     thickness=-1)

               # print('TransLat: ', np.array(approx).astype(np.float32))
               retpnp, rvecs, tvecs = cv2.solvePnP(self.GlobalDisplayCoords, np.array(approx).astype(np.float32),
                                                   self.mtx, self.dist)
               RotM, J = cv2.Rodrigues(rvecs)
               print('succes: ', retpnp)
               print('TransLat: ', tvecs)
               #print('RotMat: ', self.rotationMatrixToEulerAngles(RotM))
               imgpts, jac = cv2.projectPoints(self.axis, rvecs, tvecs, self.mtx, self.dist)
               gray = self.draw(gray, np.array(approx).astype(np.float32), imgpts)
               
       #for p in range(self.SmoothRefPos.shape[0]):
       #    gray = cv2.circle(gray, (self.SmoothRefPos[p,0].astype(np.int),self.SmoothRefPos[p,1].astype(np.int)), radius=10, color=(200, 0, 255), thickness=-1)


       #gray = cv2.circle(gray, (self.SmoothTarPos[0].astype(np.int),self.SmoothTarPos[1].astype(np.int)), radius=5, color=(200, 0, 255), thickness=1)
       #self.DisplayEdges.emit(self.SmoothTarPos)


       if self.EyeTrackEnabled:
       #for p in range(self.GazePosRight.shape[0]):
       #    gray = cv2.circle(gray, (self.GazePosRight[p,0], self.GazePosRight[p,1]), radius=5, color=(150, 0, 150), thickness=-1)
           gray = cv2.circle(gray, (self.GazePosRight[0], self.GazePosRight[1]), radius=5, color=(150, 0, 150), thickness=-1)
           gray = cv2.circle(gray, (self.GazePosLeft[0], self.GazePosLeft[1]), radius=15, color=(150, 0, 150), thickness=1)

       #for p in range(self.GazePosLeft.shape[0]):
       #    gray = cv2.circle(gray, (self.GazePosLeft[p,0], self.GazePosLeft[p,1]), radius=15, color=(150, 0, 150), thickness=1)


       self.filewriter.write('{"fame":'+str(SceneFrame) + ',"gleft":'+str(self.GazePosLeft[0])+ ',"gright":'+str(self.GazePosRight[0])+'}\n')


       if ret == True:
           cv2.imshow('Frame',gray)

           #self.result.write(gray)

       if SceneFrame >= self.CurrMaxFrame: 
           if self.currentVideoInd < len(self.videos)-1:    
               self.NextVideo()
           else: 
               self.Showfinished.emit()
       #if SceneFrame >= 800:
       #    print('SaveBitch')
       #    self.result.release()
       #    self.Showfinished.emit()

   # Offile processing of scene images
   def ProcessSceneFrame4Pos(self):
       #self.VideoCapSetup()
       while (self.cap.isOpened()):
           contoursFrame = np.zeros((540, 960), dtype=np.uint8)


           ret, frame = self.cap.read()
           SceneFrame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
           self.SceneFrameCount += 1

           if SceneFrame >= self.CurrMaxFrame-1 or ret == False:
               print('Next Video')
               if self.currentVideoInd < len(self.videos) - 1:
                   self.NextVideo()
                   return
               else:
                   self.Showfinished.emit()
                   return

          # print(frame.shape)
          # print('Scene PTS:', Scenepts)

           resizdFrame = cv2.resize(frame, (960, 540))
           gray = cv2.cvtColor(resizdFrame, cv2.COLOR_BGR2GRAY)

           h, w = gray.shape[:2]
           newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (w, h), 1, (w, h))
           gray = cv2.undistort(gray, self.mtx, self.dist, None, newcameramtx)

            #gray= cv2.GaussianBlur(gray, (25,25), 0)
           edges = cv2.Canny(gray, 100, 200, 3, L2gradient=True)

           cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

           for cnt in cnts:
               # Perimeter of the closed contours
               perimeter = cv2.arcLength(cnt, True)

               if (perimeter) < 200 or (perimeter) > 3000:
                   continue
               # contoursFrame = cv2.drawContours(contoursFrame, [cnt], 0, (255, 0, 255), 1)

               epsilon = 0.05 * perimeter
               approx = cv2.approxPolyDP(cnt, epsilon, True)

               area = cv2.contourArea(cnt)
               areaPeriRatio = area / perimeter
               if approx.shape[0] == 4 and areaPeriRatio > 10:
                   # print(area/perimeter)
                   contoursFrame = cv2.drawContours(contoursFrame, [approx], 0, (255, 0, 255), 1)
                   # for p in range(approx.shape[0]):
                   # gray = cv2.circle(gray, (approx[p,0,0],approx[p,0,1]), radius=10, color=(255, 0, 255), thickness=-1
                   self.UpdateDispPos(approx)

                   area = cv2.contourArea(cnt)
                   areaPeriRatio = area / perimeter

                   print(area / perimeter)

                   contoursFrame = cv2.drawContours(contoursFrame, [approx], 0, (255, 0, 255), 1)
                   for p in range(self.SmoothDispPos.shape[0]):
                       gray = cv2.circle(gray, (self.SmoothDispPos[p,0].astype(np.int),self.SmoothDispPos[p,1].astype(np.int)), radius=10, color=(255, 0, 255),
                                          thickness=-1)

                   # print('TransLat: ', np.array(approx).astype(np.float32))
                   retpnp, rvecs, tvecs = cv2.solvePnP(self.GlobalDisplayCoords, np.array(self.SmoothDispPos).astype(np.float32),
                                                         self.mtx, self.dist)
                   RotM, J = cv2.Rodrigues(rvecs)
                   print('succes: ', retpnp)
                   print('TransLat: ', tvecs)
                   print('RotMat: ', self.rotationMatrixToEulerAngles(RotM))

                   imgpts, jac = cv2.projectPoints(self.axis, rvecs, tvecs, self.mtx, self.dist)
                   gray = self.draw(gray, np.array(approx).astype(np.float32), imgpts)

           if ret == True:
               # Display the resulting frame
               try:

                   cv2.imshow('Frame', gray)
                   cv2.imshow('FrameRGB', edges)
                   cv2.imshow('contours', contoursFrame)

                   # cv2.imshow('Frame',newframe)
               except OSError as error:
                   print(error)

               # oldframe = newframe;
               # Press Q on keyboard to  exit
               if cv2.waitKey(25) & 0xFF == ord('q'):
                   break

   def draw(self, img, corners, imgpts):
       corner = tuple(corners[2].ravel())
       img = cv2.line(img, tuple(imgpts[0].ravel()), tuple(imgpts[1].ravel()), (155, 250, 250), 1)
       img = cv2.line(img, tuple(imgpts[0].ravel()), tuple(imgpts[2].ravel()), (200, 255, 200), 1)
       img = cv2.line(img, tuple(imgpts[0].ravel()), tuple(imgpts[3].ravel()), (200, 200, 255), 3)
       return img

   def NextVideo(self):    
       self.cap.release()
       self.currentVideoInd += 1 
       self.VideoCapSetup()

   def EndShow(self):
       self.cap.release()
       cv2.destroyAllWindows()
       self.filewriter.close()

   def VideoCapSetup(self):
       self.EyePts = 0
       self.cap = cv2.VideoCapture(self.videos[self.currentVideoInd])

       if (self.cap.isOpened()== False):
           print("Error opening video stream or file")
       
       self.CurrMaxFrame = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
       print("Toral Frames: ", self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) 

   def UpdateDispPos(self, approx):

       edgePoints = np.squeeze(approx)
       meanP = np.mean(edgePoints, axis = 0)
       quadrants = np.sign(edgePoints-meanP)
       # depending on the relative positions of reference points
       SortingRef=  quadrants[:,0] +quadrants[:,1]*2
       sorted_Poses = edgePoints[np.argsort(SortingRef)]

       beta = 640/3840
       alpha = 360/2160

       self.SmoothDispPos = self.SmoothDispPos*(1-self.MovingDispContrib)  + sorted_Poses*self.MovingDispContrib
       #self.SmoothDispPos = self.SmoothDispPos * (1 - self.MovingDispContrib) + edgePoints * self.MovingDispContrib


   def UpdateTarPos(self, approx):

       edgePoints = np.squeeze(approx)
       meanP = np.mean(edgePoints, axis=0)


       self.SmoothTarPos = self.SmoothTarPos * (1 - self.MovingDispContrib) + meanP * self.MovingDispContrib

   def EnableSynch(self, state):
       if state == Qt.Checked:
           self.SyncEnabled = True
           print('Synching enabled')
       else:
           self.SyncEnabled = False
           print('Synching disabled')

   def EnableET(self, state):
       if state == Qt.Checked:
           self.EyeTrackEnabled = True
           print('Tracking enabled')
       else:
           self.EyeTrackEnabled = False
           print('Tracking disabled')

   def SetVideoFiles(self, VideoList):
       self.videos = VideoList
       print(VideoList)

       self.VideoCapSetup()
       self.cap.set(cv2.CAP_PROP_POS_FRAMES, 800 // 2)

   def rotationMatrixToEulerAngles(self, R):
       sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
       singular = sy < 1e-6
       if not singular:
           x = math.atan2(R[2, 1], R[2, 2])
           y = math.atan2(-R[2, 0], sy)
           z = math.atan2(R[1, 0], R[0, 0])
       else:
           x = math.atan2(-R[1, 2], R[1, 1])
           y = math.atan2(-R[2, 0], sy)
           z = 0
       return np.array([x, y, z]) * 180 / np.pi

   @pyqtSlot(np.ndarray)
   def UpdateTSscene(self, TSs):
       self.sceneTSArray = TSs

   @pyqtSlot(float)   
   def UpdateEyePts (self, Eyepts):
       self.EyePts = Eyepts

   @pyqtSlot(np.ndarray)   
   def UpdateGazePositionRight (self, Gaze2D):
       #print('Gaz2DDe', Gaze2D)
       self.GazePosRight = Gaze2D.astype(int)
       #self.GazePos = [self.GazePos[0,0], self.GazePos[1,0]]
       #print('Gazzee', [self.GazePos[0,0], self.GazePos[1,0]])

   @pyqtSlot(np.ndarray)   
   def UpdateGazePositionLeft (self, Gaze2D):
       #print('Gaz2DDe', Gaze2D)
       self.GazePosLeft = Gaze2D.astype(int)
       #self.GazePos = [self.GazePos[0,0], self.GazePos[1,0]]
       #print('Gazzee', [self.GazePos[0,0], self.GazePos[1,0]])