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

class ShowEyes():
    print('Hey Lets go disco!!')
