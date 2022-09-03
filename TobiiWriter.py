from queue import Queue, Empty
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

import time

class TobiiWriter(QObject):
    TobiiWriterfinished = pyqtSignal()

    def __init__(self, GstreamWorker, dataofinterest):
        super().__init__()
        self.startWriters = False
        self.dowork = True
        self.IMUorGaze = True
        self.GstreamWorker = GstreamWorker

        self.namestring = ""
        self.path = ""
        self.timestr = ""

        self.queue = Queue()
        self.dataofinterest = dataofinterest

        if  self.dataofinterest  == 1:     # IMU data
            self.GstreamWorker.IMU_signal.connect(self.writequeue)
        elif self.dataofinterest  == 2: # Gaze data
            self.GstreamWorker.Gaze_signal.connect(self.writequeue)
        elif self.dataofinterest  == 3: # Video timestamp data
            self.GstreamWorker.TS_signal.connect(self.writequeue)
            self.GstreamWorker.TTL_signal.connect(self.writequeue)

        self.GstreamWorker.Gstreamfinished.connect(self.close)


    def setWriters (self, namestring, timestr, path):
        if self.dataofinterest == 1:
            self.filewriter = open(path + '/IMUdata-' + namestring + timestr + ".txt", 'w')
        elif self.dataofinterest  == 2:
            self.filewriter = open(path + '/Gazedata-' + namestring + timestr + ".txt", 'w')
        elif self.dataofinterest  == 3:
            self.filewriter = open(path + '/TSdata-' + namestring + timestr + ".txt", 'w')

        self.startWriters = True
        print('Name Set', self.startWriters)

    def PauseWriters(self):
        self.startWriters = False

    def UnPauseWriters(self):
        self.startWriters = True

    def internal_writer(self):
        print('Saving thread running',self.startWriters)
        while self.dowork:
            #print(self.startWriters)
            try:
                data = self.queue.get(True, 1)

                #print(data)

            except Empty:
                #print('no!')

                continue    
            
            #with self.filewriter as file:
            #    self.filewriter.write(data)
            if self.startWriters == True:
                self.filewriter.write(data)
                self.queue.task_done()


        self.TobiiWriterfinished.emit()



    def close(self):
        self.queue.join()
        #self.GazeQueue.join()

        self.startWriters = False
        self.dowork = False
        #time.sleep(2)
        self.filewriter.close()
        #self.Gazefilewriter.close()

        #self.deleteLater()


    #@pyqtSlot(string)
    def writequeue(self, data):
        self.queue.put(data)
        #print('Come string', data)


