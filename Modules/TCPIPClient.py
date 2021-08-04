
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


global ModuleDir
ModuleDir = "Modules/"

print('yo')


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


   def CommunWork(self):

       self.TcpSocket.connect((self.HOST, self.PORT))

       while  self.continue_run:
           data = self.TcpSocket.recv(8)
           self.TcpSocket.sendall(b'Hi')

           if len(data) <= 0:
               break
           #self.window.MessageLine.setText(repr(data))
           self.MessRecieved.emit(repr(data))
           print('Received', repr(data))

       self.TCPfinished.emit()

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
class TCPIPClient(QObject):
  
   def __init__(self, GstreamWorker):

       super().__init__()
       print('TCP IP Client is here!!')  

       self.window = WindowArrangment()
       self.window.show()
       
                
       HOST = '10.120.12.242'  # The server's hostname or IP address
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

   @pyqtSlot(str)   
   def UpdateMessage(self, meassage):

       self.window.MessageLine.setText(meassage)

