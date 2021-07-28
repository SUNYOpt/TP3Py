
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
   
    
   #self.GstreamWorker = TP3py_Gstream()
   # Visual Arrangment of the GUI 
   def __init__(self, GstreamWorker):

       super().__init__()

       print('TCP IP Client is here!!')  

       self.window = WindowArrangment()
       self.window.show()
       



       self.Tcpthread = QThread()
       self.Tcpthread.started.connect(self.TCPWorker)
       self.window.startbutton.clicked.connect(self.Tcpthread.start)

    ############### BUG BUGG lol:))
   def TCPWorker(self):

         
       HOST = '10.120.12.242'  # The server's hostname or IP address
       PORT = 55000            # The port used by the server

       self.TcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.TcpSocket.connect((HOST, PORT))
       self.TcpSocket.sendall(b'Hello, world babe')

       # not the best way!!!!
       while True:
           data = self.TcpSocket.recv(8)
           if len(data) <= 0:
               break
           self.window.MessageLine.setText(repr(data))
           print('Received', repr(data))


       print('Closing connection')       
       self.TcpSocket.close()



