from PyQt5.QtWidgets import QMainWindow, QListWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget

global ModuleDir
ModuleDir = "Modules/"

print('yo')
class RandomPlot():

   # Visual Arrangment of the GUI 
   def WindowOrg(self, QMainWindow):
       self.setWindowTitle('Random Plot')
       #self.setFixedSize(1200, 600)

       # Set the central widget
       self._centralWidget = QWidget(self)
       self.generalLayout =  QGridLayout()
       self.setCentralWidget(self._centralWidget)
       self._centralWidget.setLayout(self.generalLayout)

   def __init__(self):

       super().__init__()

       print('Hey Lets go disco!!')  

       window = self.WindowOrg(QMainWindow)
       window.show()
       

       
       
