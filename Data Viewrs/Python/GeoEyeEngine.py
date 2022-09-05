import numpy as np
import cv2
from itertools import combinations
import json
from json import JSONEncoder
import sys



class GeometryVars:

  def __init__(self, center, TMat, DispCoors):
    super().__init__()    
    self.center = center
    self.TMat = TMat
    self.DispCoors = DispCoors
    # k: metric coefficient of the Riemannian space centered on the ref. point


# subclass JSONEncoder
class GeoVarsEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.ndarray):
      return obj.tolist()
    return JSONEncoder.default(self, obj)

class GeoEyeEngine:

  def __init__(self, RightLeft):
    super().__init__()    
    self.RightLeft = RightLeft
    # Number of reference points
    self.RefPnum = 5 
    self.RefNamesV1 = ['RefP1v1','RefP2v1','RefP3v1','RefP4v1','RefP5v1']
    self.RefNamesV2 = ['RefP1v2','RefP2v2','RefP3v2','RefP4v2','RefP5v2']

    # The corresponding ref. points in the triangles

    # Calibrated reference structures of the first video
    self.RefP1 = [GeometryVars((1,1), 1, (1,1)) for i in range(self.RefPnum)]
    # Calibrated reference structures of the second video
    self.RefP2 = [GeometryVars((2,2), 2, (2,2)) for i in range(self.RefPnum)]


    self.calibrated = False


  def CalD(self, centerE1, centerE2): 

    
    for i in range(self.RefPnum):
        D1 = np.dot(self.RefP1[i].TMat, np.subtract(self.RefP1[i].center,centerE1))
        D2 = np.dot(self.RefP2[i].TMat, np.subtract(self.RefP2[i].center,centerE2))

        self.dv1[i] = np.sqrt(D1.dot(D1))
        self.dv2[i] = np.sqrt(D2.dot(D2))


    if self.calibrated == True:
        print('Tracking based on pupil ... Todo')





  def SetRefGeo(self, center1, center2, TMat1, TMat2, DisPoint, pos):
    self.RefP1[pos-1] = GeometryVars(center1, TMat1, DisPoint)
    self.RefP2[pos-1] = GeometryVars(center2, TMat2, DisPoint)


  def SaveRPStructures(self):
   
    #print(GeoVarsEncoder().encode(self.RefP1))
    #print(self.RefP1.__dict__)
    AllRPs = {}
    counter = 0
    for name in self.RefNamesV1:
        AllRPs[name] = self.RefP1[counter].__dict__
        counter += 1

    counter = 0
    for name in self.RefNamesV2:
        AllRPs[name] = self.RefP2[counter].__dict__
        counter += 1

    json_dump = json.dumps(AllRPs, cls=GeoVarsEncoder)
    print(json_dump)

    with open(self.RightLeft+'mydata.json', 'w') as f:
      json.dump(json_dump, f)
    
     #jsonStr = json.dumps(self.RefP1.__dict__)


  def LoadRPStructures(self):
    f = open(self.RightLeft+'mydata.json')
    Calibdata = json.loads(json.load(f))
    f.close()

    counter = 0
    for name in self.RefNamesV1:
        print(name)
        self.RefP1[counter] = GeometryVars(Calibdata[name]['center'], Calibdata[name]['TMat'], \
           Calibdata[name]['DispCoors'])
        counter += 1

    
    counter = 0
    for name in self.RefNamesV2:
        self.RefP2[counter] = GeometryVars(Calibdata[name]['center'], Calibdata[name]['TMat'], \
           Calibdata[name]['DispCoors'])
        counter += 1
    
    self.DispArea = self.AreaMeasure(self.RefP1[0], self.RefP1[1], self.RefP1[2])+ \
        self.AreaMeasure(self.RefP1[3], self.RefP1[1], self.RefP1[2])
    print('Disp Area',self.DispArea)

    PLN = self.PairListNumel
    print('PLN', PLN)
    Tcounter = 0
    for (x,y) in self.TrianglePairsListV1:
        self.Tcompute[Tcounter] = TriangleCompute(self.RefP1[x-1],self.RefP1[y-1])
        self.Tcompute[Tcounter+PLN] = TriangleCompute(self.RefP2[x-1],self.RefP2[y-1])
        Tcounter += 1

    self.calibrated = True

    #print('K1', self.Tcompute13.k1)


  def AreaMeasure(self, RefP1, RefP2, RefP3):   

    JointV = np.subtract(RefP1.DispCoors,RefP2.DispCoors)
    LBase12 = np.sqrt(JointV.dot(JointV))   
       
    JointV = np.subtract(RefP1.DispCoors,RefP3.DispCoors)
    LBase13 = np.sqrt(JointV.dot(JointV))   
        
    JointV = np.subtract(RefP2.DispCoors,RefP3.DispCoors)
    LBase23 = np.sqrt(JointV.dot(JointV))   

    halfperimeter = (LBase12+LBase13+LBase23)/2

    return np.sqrt(halfperimeter*(halfperimeter-LBase12)*(halfperimeter-LBase13)*\
        (halfperimeter-LBase23))