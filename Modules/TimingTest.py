# Timing Test Module 
# Modular Streaming Pipeline of Eye/Head Tracking Data Using Tobii Pro Glasses 3
# Hamed Rahimi Nasrabadi, Jose-Manuel Alonso
# bioRxiv 2022.09.02.506255; doi: https://doi.org/10.1101/2022.09.02.506255

from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import numpy
import socket
import sys



#########################
"""TCP IP Worker Class"""
#########################
class TCPWorkerClass(QObject):
   TCPfinished = pyqtSignal()  # give worker class a finished signal
   MessRecieved = pyqtSignal(str)

   def __init__(self, HOST, PORT):

       super().__init__()
       self.continue_run = True 

       self.HOST= HOST
       self.PORT = PORT
       self.TcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

       self.TTLsendMess = False

   def CommunWork(self):

       self.TcpSocket.connect((self.HOST, self.PORT))
       self.TcpSocket.sendall(b'H') # For hand Shake
       while  self.continue_run:
           data = self.TcpSocket.recv(8)

           #self.window.MessageLine.setText(repr(data))
           if data:
               self.MessRecieved.emit(repr(data))
               print('Received', repr(data))

           if data == b't':
               self.TcpSocket.sendall(b'o')
               break
       self.TCPfinished.emit()
   def SendTTL(self):
       print("in")
       self.TTLsendMess = True
       if self.continue_run:
           self.TcpSocket.sendall(b'g')
       
   def EndCommun(self):
       self.continue_run = False
       print('Closing connection')       
       self.TcpSocket.close()

########################################################################
#Visual arrangment and the things we'd like to have on the module's GUI#
########################################################################
class WindowArrangment(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Show Eyes')
        #self.setFixedSize(1200, 600)

        # Set the central widget
        self._centralWidget = QWidget(self)
        self.generalLayout =  QGridLayout()
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self.generalLayout.addWidget(QLabel('Server Message:'), 0, 0)
        self.MessageLine = QLineEdit()
        self.generalLayout.addWidget(self.MessageLine, 1, 0)
        self.startbutton = QPushButton('start experiment')
        self.generalLayout.addWidget(self.startbutton, 2, 0)


######################################################
#The Class definition that we load in the main thread#
######################################################
class TimingTest(QObject):
  
   def __init__(self, GstreamWorker):

       super().__init__()
       print('TCP IP Client is here!!')  

       self.window = WindowArrangment()
       self.window.show()
       
                
       HOST = '10.117.3.5'  # The server's hostname or IP address
       PORT = 55000            # The port used by the server


       self.Tcpthread = QThread()
       
       TCPWorker = TCPWorkerClass(HOST,PORT)

       TCPWorker.moveToThread(self.Tcpthread)

       # Cleaning up once the communication ends
       TCPWorker.TCPfinished.connect(self.Tcpthread.quit) 
       TCPWorker.TCPfinished.connect(TCPWorker.deleteLater)  
       self.Tcpthread.finished.connect(self.Tcpthread.deleteLater) 


       self.Tcpthread.started.connect(TCPWorker.CommunWork)
       self.Tcpthread.finished.connect(TCPWorker.EndCommun)

       self.window.startbutton.clicked.connect(self.Tcpthread.start)

       TCPWorker.MessRecieved.connect(self.UpdateMessage)

       self.Tcpthread.TCPWorker = TCPWorker


       # Connecting TTL signal of the Gstreamer worker
       self.GstreamWorker = GstreamWorker
       self.GstreamWorker.TTL_signal.connect(self.ProcessTTL)


   @pyqtSlot(str)   
   def UpdateMessage(self, meassage):
       self.window.MessageLine.setText(meassage)

   @pyqtSlot(str)
   def ProcessTTL(self, meassage):
       TTLind = meassage.find("value")
       if TTLind > 0:
           print(str(meassage[-3:-2]))
           if str(meassage[-3:-2]) == '1':
               self.Tcpthread.TCPWorker.SendTTL()

   def close(self):
       # Closing the window
       self.Tcpthread.TCPWorker.EndCommun()
       self.window.close()