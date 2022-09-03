
from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import numpy
import cv2
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap


global ModuleDir
ModuleDir = "Modules/"

print('yo')



########################################################################
#Visual arrangment and the things we'd like to have on the module's GUI#
########################################################################
class WindowArrangment(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Show Scene')
        #self.setFixedSize(1200, 600)

        # Set the central widget
        self._centralWidget = QWidget(self)
        self.generalLayout =  QGridLayout()
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)


        self.disply_width = 512
        self.display_height = 512
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        self.generalLayout.addWidget(self.image_label, 1, 1)

######################################################
#The Class definition that we load in the main thread#
######################################################
class ShowScene(QObject):
   
    
   #self.GstreamWorker = TP3py_Gstream()
   # Visual Arrangment of the GUI 
   def __init__(self, GstreamWorker):

       super().__init__()

       print('Hey Lets go Eye disco!!')  

       self.window = WindowArrangment()
       self.window.show()
       
       self.GstreamWorker = GstreamWorker

       self.GstreamWorker.SceneVideo_signal.connect(self.update_image)


   def close(self):
       # Closing the window
       self.window.close()


   @pyqtSlot(numpy.ndarray)   
   def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.window.image_label.setPixmap(qt_img)
    
   def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        ##### COLOR_YUV2RGB_NV12 COLOR_YUV420p2BGR COLOR_YUV420sp2RGB
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_YUV420p2BGR)
        #rgb_image = cv_img
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.window.disply_width, self.window.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

