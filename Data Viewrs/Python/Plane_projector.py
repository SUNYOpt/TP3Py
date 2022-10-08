import numpy as np
import cv2
from functools import reduce


class GeoVars:
  def __init__(self, center, W, H, Ecc, Orien):
    super().__init__()    
    self.center = center
    self.w = W
    self.h = H
    self.ecc = Ecc
    self.ori = Orien * np.pi /180  

class Plane_projector:
  
  def __init__(self, LeftRight):
    super().__init__()    
    self.LeftRight = LeftRight
    if self.LeftRight == 'Left':
        self.Thresholds = [230, 200]

    if self.LeftRight == 'Right':
        self.Thresholds = [160, 200]

    self.dilatation_size = 5
    # for the first and second videos of an eye
    self.EyeGeo1 = GeoVars((0,0), 1, 1, 1, 0)
    self.EyeGeo2 = GeoVars((0,0), 1, 1, 1, 0)
 
    self.Ghull1 = []
    self.Ghull2 = []
    self.TmatArray1 = []
    self.TmatArray2 = []
    self.currFrame = 0
    self.Calibmode = False

  def TrackPupils (self, inImg1, inImg2, countImg, currFrame, GeoEng, DisPoint):
       self.currFrame = currFrame
       # First image of right eye
       self.ImInter1 = 255-inImg1
       element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * self.dilatation_size + 1, 2 * self.dilatation_size + 1),
                                       (self.dilatation_size, self.dilatation_size))
       self.ImInter1 = cv2.dilate(self.ImInter1, element)
       ImgR1Tresh = (self.ImInter1 > self.Thresholds[0]) *220
       self.TrackPupil(ImgR1Tresh.astype(np.uint8),1)
         
       # Second image of right eye
       self.ImInter2 = 255-inImg2
       element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * self.dilatation_size + 1, 2 * self.dilatation_size + 1),
                                      (self.dilatation_size, self.dilatation_size))
       self.ImInter2 = cv2.dilate(self.ImInter2, element)
       ImgR1Tresh = (self.ImInter2 > self.Thresholds[1]) *220
       self.TrackPupil(ImgR1Tresh.astype(np.uint8),2)

       # Drawing contours of segmented pupil
       #print('Hull:', len(self.Ghull1) == 0)
       if len(self.Ghull1) != 0:
           self.ImInter1 = cv2.drawContours(self.ImInter1, [self.Ghull1], 0, (255, 0, 255), 1)
       if len(self.Ghull2) != 0:
           self.ImInter2 = cv2.drawContours(self.ImInter2, [self.Ghull2], 0, (255, 0, 255), 1)
       self.ImInter1 = cv2.circle(self.ImInter1, (int(self.EyeGeo1.center[0]),int(self.EyeGeo1.center[1])), radius=2, color=(255, 0, 255), thickness=-1)
       self.ImInter2 = cv2.circle(self.ImInter2, (int(self.EyeGeo2.center[0]),int(self.EyeGeo2.center[1])), radius=2, color=(255, 0, 255), thickness=-1)
      


       if self.Calibmode == True:
           # calibration frame index
           f = int(self.currFrame - self.CalibStratFrame)
           self.DisPointArray.append(DisPoint)
           # When the certain frames passed
           if self.currFrame >=  self.CalibStratFrame+self.Calibnumframes:
               self.Calibmode = False
               # Averaging
               Tmat1Ave =reduce(lambda a, b: a + b, self.TmatArray1) / len(self.TmatArray1)
               Tmat2Ave =reduce(lambda a, b: a + b, self.TmatArray2) / len(self.TmatArray2)
               C1 = tuple(map(np.mean, zip(*self.centerArray1)))
               C2 = tuple(map(np.mean, zip(*self.centerArray2)))
               DisPoint = reduce(lambda a, b: a + b, self.DisPointArray) / len(self.DisPointArray) 

               print('T1:', Tmat1Ave)
               print('T2:', Tmat2Ave)
               print('C1:', C1)
               print('C2:', C2)
               print('Dp:', DisPoint)
               GeoEng.SetRefGeo(C1, C2, Tmat1Ave, Tmat2Ave, DisPoint, self.currPos)
           else:
               self.ShowGeoCount (countImg,f)




       GeoEng.CalD(self.EyeGeo1.center, self.EyeGeo2.center)


  def TrackPupil (self, inImg, imagenumber):

        inImg = cv2.Canny(inImg,150,200,3, L2gradient=True)

        cnts, _ = cv2.findContours(inImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        for cnt in cnts:   
          
          hull = cv2.convexHull(cnt)
          perimeter = cv2.arcLength(hull,True)
          if (perimeter)  < 40 or (perimeter)  > 300 or hull.shape[0] < 10:
            continue

          ellipse = cv2.fitEllipse(hull)
          widthE = ellipse[1][0]
          heightE = ellipse[1][1]  
          centerE = ellipse[0]
          rotation = ellipse[2]
          
          if heightE>widthE:
            eccenE =  np.sqrt(1-widthE**2/heightE**2)
          elif heightE<widthE:
            eccenE =  np.sqrt(1-heightE**2/widthE**2)
          else:
            eccenE = 0
        

          if (widthE*heightE) < 4000 and eccenE <0.8 and  centerE[1] > 20 and (widthE*heightE) > 700:
               #print('Hull:', hull)
               if imagenumber == 1:
                   self.EyeGeo1 = GeoVars(centerE,widthE,heightE,eccenE,rotation)
                   self.Ghull1 = hull                   
               else:
                   self.EyeGeo2 = GeoVars(centerE,widthE,heightE,eccenE,rotation)
                   self.Ghull2 = hull

  def ShowGeoContAve (self, currframe, numframes, currPos):
       self.Calibmode = True
       # initialization
       self.TmatArray1 = []
       self.TmatArray2 = []
       self.centerArray1 = []
       self.centerArray2 = []
       self.DisPointArray = []
       self.CalibStratFrame = currframe
       self.Calibnumframes  = numframes
       self.currPos = currPos

  def ShowGeoCount (self, countImg, f):
       
       self.TMat1 = self.getTransfomMat(self.EyeGeo1)
       self.TMat2 = self.getTransfomMat(self.EyeGeo2)

       self.TmatArray1.append(self.TMat1)
       self.TmatArray2.append(self.TMat2)
       
       self.centerArray1.append(self.EyeGeo1.center)
       self.centerArray2.append(self.EyeGeo2.center)

       DiffVector1 = np.transpose(np.squeeze(np.subtract([self.Ghull1],self.EyeGeo1.center)),(1,0))     
       Transformed1 = np.add(np.transpose(np.dot(self.TMat1, DiffVector1),(1,0)),self.EyeGeo1.center)     
       remappedCount1 = [np.array(Transformed1).astype(np.int32)]
       
       DiffVector2 = np.transpose(np.squeeze(np.subtract([self.Ghull2],self.EyeGeo2.center)),(1,0))     
       Transformed2 = np.add(np.transpose(np.dot(self.TMat2, DiffVector2),(1,0)),self.EyeGeo2.center)     
       remappedCount2 = [np.array(Transformed2).astype(np.int32)]

       #countImg[:, :256] = cv2.drawContours(countImg[:, :256], [self.Ghull1], 0, (255, 0, 255), 1)
       countImg[:, :256]  = cv2.drawContours(countImg[:, :256], remappedCount1, 0, (255, 0, 255), 1)
      
       #countImg[:, 256:512] = cv2.drawContours(countImg[:, 256:512], [self.Ghull2], 0, (255, 0, 255), 1)
       countImg[:, 256:512]  = cv2.drawContours(countImg[:, 256:512], remappedCount2, 0, (255, 0, 255), 1)

  def getTransfomMat (self, EyeGeo):

       # only for showing the remapped contours
       TScal = 40

       self.RotMat = [[np.cos(EyeGeo.ori), np.sin(EyeGeo.ori)], \
           [np.sin(EyeGeo.ori), -np.cos(EyeGeo.ori)]]
     
       alpha = np.arccos(EyeGeo.ecc)
       targetSize = EyeGeo.h/np.sin(alpha)

       self.ScaleMat = [[targetSize/TScal, 0],[0, EyeGeo.h/TScal]]

       return np.matmul(self.ScaleMat, self.RotMat)