# A sample code of a module and its functions

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from functools import partial
from datetime import datetime
from TobiiExtract import TobiiExtract
from TP3py_Gstream import TP3py_Gstream

global ModuleDir
ModuleDir = "Modules/"

""" 
In general we would like to have a class like TP3PyMod.py to inherit its methods in the modules:
class ShowEyes(TP3PyMod):
This sample code shows some of the methods we would need
"""

class ShowEyes():
    print('Hey Lets go disco!!')


    """ 
    Initialization would setup the following feature:
    - Visual features: setting up the arrangment and properties of the PyQt5 widgets
    (for instance a

    """
    def __init__(self, parent=None):
        



    """ 
    The start method would be activated when the recording starts. 
    This method controls how the data is being processed and presented 
    which would be heavily relied on the application that user wants to creat
    """
    def start(self, ):
        


    """ 
    The end method would deactivate the thread and colses all the files and processes 
    """
    def end(self, ):
        


    """ 
    Save method would be needed to let people save their processed data
    """
    def save(self, ):
        


        

    """ 
    PresentResults supplies the users with the set of functions for real-time visualization
    of data in a form of plot or video within the window of the module being set in the initiallization
    """
    def PresentResults(self, ):
        
