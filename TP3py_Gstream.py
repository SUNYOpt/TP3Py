# TP3Py Pipeline - Gstreamer Class 
# Modular Streaming Pipeline of Eye/Head Tracking Data Using Tobii Pro Glasses 3
# Hamed Rahimi Nasrabadi, Jose-Manuel Alonso
# bioRxiv 2022.09.02.506255; doi: https://doi.org/10.1101/2022.09.02.506255


import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstApp", "1.0")
import json
from collections import namedtuple
import matplotlib.animation as animation
import sys
import os
import cv2
import numpy
from datetime  import datetime
from gi.repository import GstApp, GLib, GObject, Gst
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from TobiiWriter import TobiiWriter
import time
import requests
from requests.auth import HTTPBasicAuth
import websocket
import asyncio 
Gst.init(None)


class TP3py_Gstream(QObject):
    
    """Set of signals for outputting the data being streamed to other threads"""   
    # give worker class a finished signal
    Gstreamfinished = pyqtSignal()
    # Signal containing eye video frame
    EyeVideo_signal = pyqtSignal(numpy.ndarray)
    # Signal containing scene video frame
    SceneVideo_signal = pyqtSignal(numpy.ndarray)
    # Signal containing IMU data
    IMU_signal = pyqtSignal(str)
    # Signal containing Gaze data
    Gaze_signal = pyqtSignal(str)
    # Signal containing Timestamps - PTS
    TS_signal = pyqtSignal(str)
    # Signal containing TTL data
    TTL_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        #super().__init__()
        self.continue_run = True  # provide a bool run condition for the class
        self.elapsedTime = 0
        # Default values of experiment names and Initials
        self.ExpNamestring = ""
        self.InitialNamestring = "Test"
        # Parent directory
        self.parent_dir = os.path.join(os.path.expanduser('~'), 'EyeTracking', 'Data')


        # Setting up the Tobii exr=tractor thread- for saving and signaling IMU, EyeTracker, etc..
        self.TobiiWriteThread = QThread()
        self.TobiiGazeWriteThread = QThread()
        self.TobiiTSWriteThread = QThread()

        TobiiWriteWorker = TobiiWriter(self, 1)
        TobiiGazeWriteWorker = TobiiWriter(self, 2)
        TobiiTSWriteWorker = TobiiWriter(self, 3)

        TobiiWriteWorker.moveToThread(self.TobiiWriteThread)
        TobiiGazeWriteWorker.moveToThread(self.TobiiGazeWriteThread)
        TobiiTSWriteWorker.moveToThread(self.TobiiTSWriteThread)

        # Cleaning up once the communication ends
        TobiiWriteWorker.TobiiWriterfinished.connect(self.TobiiWriteThread.quit)
        TobiiWriteWorker.TobiiWriterfinished.connect(TobiiWriteWorker.deleteLater)
        self.TobiiWriteThread.finished.connect(self.TobiiWriteThread.deleteLater)

        # Cleaning up once the communication ends
        TobiiGazeWriteWorker.TobiiWriterfinished.connect(self.TobiiGazeWriteThread.quit)
        TobiiGazeWriteWorker.TobiiWriterfinished.connect(TobiiGazeWriteWorker.deleteLater)
        self.TobiiGazeWriteThread.finished.connect(self.TobiiGazeWriteThread.deleteLater)
        
        TobiiTSWriteWorker.TobiiWriterfinished.connect(self.TobiiTSWriteThread.quit)
        TobiiTSWriteWorker.TobiiWriterfinished.connect(TobiiTSWriteWorker.deleteLater)
        self.TobiiTSWriteThread.finished.connect(self.TobiiTSWriteThread.deleteLater)


        self.TobiiWriteThread.started.connect(TobiiWriteWorker.internal_writer)
        self.TobiiGazeWriteThread.started.connect(TobiiGazeWriteWorker.internal_writer)
        self.TobiiTSWriteThread.started.connect(TobiiTSWriteWorker.internal_writer)


        # Starting the thread
        self.TobiiWriteThread.start()
        self.TobiiGazeWriteThread.start()
        self.TobiiTSWriteThread.start()

        self.TobiiWriteThread.TobiiWriteWorker = TobiiWriteWorker
        self.TobiiGazeWriteThread.TobiiGazeWriteWorker = TobiiGazeWriteWorker
        self.TobiiTSWriteThread.TobiiTSWriteWorker = TobiiTSWriteWorker


                                            
        self.pipeline = Gst.parse_launch('rtspsrc location=rtsp://192.168.75.51:8554/live/all?gaze-overlay=false \
        latency=100 name=src protocols=GST_RTSP_LOWER_TRANS_TCP enable-meta=true do-timestamp=true buffer-mode = 0 drop-on-latency=true \
        src. ! application/x-rtp,payload=96 ! rtpjitterbuffer max-misorder-time = 0  ! rtph264depay ! h264parse  ! tee name=tscene \
        tscene. ! queue ! avdec_h264 ! appsink name=Appscenesink \
        tscene. ! queue ! splitmuxsink  max-size-time=60000000000  name=scenesink \
        src. ! application/x-rtp,payload=98 ! rtpjitterbuffer max-misorder-time = 0  ! rtph264depay ! h264parse  ! tee name=teye \
        teye. ! queue ! avdec_h264 ! videoscale ! video/x-raw,width=512, height=128! appsink name=Appeyesink \
        teye. ! queue ! splitmuxsink  max-size-time=60000000000  name=eyesink \
        src. ! application/x-rtp,payload=99 ! rtpjitterbuffer max-misorder-time = 0  ! appsink name=Gazesink \
        src. ! application/x-rtp,payload=100 ! rtpjitterbuffer max-misorder-time = 0 ! appsink name=TTLsink \
        src. ! application/x-rtp,payload=101 ! rtpjitterbuffer max-misorder-time = 0 ! appsink name=IMUsink ')

        self.appEyeMsink = self.pipeline.get_by_name("eyesink")
        self.appIMUsink = self.pipeline.get_by_name("IMUsink")
        self.appGazesink = self.pipeline.get_by_name("Gazesink")
        self.appEyeMsinkGUI = self.pipeline.get_by_name("Appeyesink")
        self.appScenesinkGUI = self.pipeline.get_by_name("Appscenesink")
        self.appScenesink = self.pipeline.get_by_name("scenesink")
        self.appTTLsink = self.pipeline.get_by_name("TTLsink")


        print("Gstream init. done!")

    """ Handles for accessing the first frame PTS in the video saving branch of Gstreamer"""
    def format_location_full_callback_eye (self, splitmux, fragment_id, firstsample):
        buf =firstsample.get_buffer()
        if self.continue_run:
            self.TS_signal.emit('{"eyeMSTS":'+ str(buf.pts/1e9)+'}'+'\n')

    def format_location_full_callback_scene (self, splitmux, fragment_id, firstsample):
        buf =firstsample.get_buffer()
        if self.continue_run:
            self.TS_signal.emit('{"sceneMSTS":'+ str(buf.pts/1e9)+'}'+'\n')

    """ Scene movie buffer management """
    #Emitting the video buffer in SceneVideo_signal
    def gst_to_sceneimage(self, sample):
        buf = sample.get_buffer()
        recievedTime = (buf.pts)/1e9 
        caps = sample.get_caps()

        temph = caps.get_structure(0).get_value('height')//2
        tempw = caps.get_structure(0).get_value('width')//2
        size = temph*tempw

        h = caps.get_structure(0).get_value('height')
        w = caps.get_structure(0).get_value('width')

        YUV_arr = numpy.ndarray(
            (h*3//2, w),
            buffer=buf.extract_dup(0, h*w*3//2),
            dtype=numpy.uint8)

        if self.continue_run:
            self.SceneVideo_signal.emit(YUV_arr)

        return YUV_arr, recievedTime

    def rebin(self, arr, new_shape):
        shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
        return arr.reshape(shape).max(-1).max(1)

    def SceneM_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        EyeImageBuffer, IMUtime = self.gst_to_sceneimage(sample)
        self.extractTS_scene(IMUtime)
        return Gst.FlowReturn.OK

    """ Eye movie buffer management """
    #Emitting the video buffer in EyeVideo_signal
    def gst_to_eyeimage(self, sample):
        buf = sample.get_buffer()
        recievedTime = (buf.pts)/1e9 
        caps = sample.get_caps()

        arr = numpy.ndarray(
            (caps.get_structure(0).get_value('height'),
             caps.get_structure(0).get_value('width'),
             1),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=numpy.uint8)
       
        if self.continue_run:
            self.EyeVideo_signal.emit(arr)
        return arr, recievedTime
    
    def EyeM_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        EyeImageBuffer, Eyetime = self.gst_to_eyeimage(sample)
        self.extractTS_eye(Eyetime)
        return Gst.FlowReturn.OK

    """ IMU buffer management """
    # Returns the raw output of IMU Payloads
    def gst_to_IMU(self, sample):
        buf = sample.get_buffer()
        caps = sample.get_caps()
        recievedTime = (buf.pts)/1e9
        arr = numpy.ndarray(
            (1,buf.get_size()),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=numpy.uint8)

        return bytes(arr), recievedTime

    def IMU_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        streamString, IMUtime = self.gst_to_IMU(sample)
        self.extractIMU(str(streamString), IMUtime)
        return Gst.FlowReturn.OK

    """ Gaze data buffer management """
    # Returns the raw output of Gaze and TTL Payloads
    def gst_to_Gaze(self, sample):
        buf = sample.get_buffer()
        recievedTime = (buf.pts)/1e9 
        arr = numpy.ndarray(
            (1,buf.get_size()),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=numpy.uint8)
        
        return bytes(arr), recievedTime

    def Gaze_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        streamString, IMUtime = self.gst_to_Gaze(sample)
        self.extractGazeD(str(streamString), IMUtime)
        return Gst.FlowReturn.OK

    """ TTL data buffer management """
    def TTL_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        streamString, IMUtime = self.gst_to_Gaze(sample)
        self.extractTTL(str(streamString), IMUtime)
        return Gst.FlowReturn.OK

    def do_work(self):

        # Initialize the path were files are being saved   datetime.today().strftime('%Y%m%d%H%M')
        self.path = os.path.join(self.parent_dir, self.InitialNamestring)
        # Create the subject directory
        try:
            os.mkdir(self.path)
        except OSError as error:
            print(error)
        self.path = os.path.join(self.path , datetime.today().strftime('%Y%m%d%H%M'))
        self.timestr = datetime.today().strftime('-%H-%M')
        # Create the experiment directory as a subdirectory of the subject folder
        try:
            os.mkdir(self.path)
        except OSError as error:
            print(error)


        """
        Saving the scene and eye movies right away in a segmented manner while keeping the first frame timestamps
        """
        self.appEyeMsink.set_property('location',  self.path+'/eye-'+self.ExpNamestring+self.timestr+"-%d.mov")
        self.appEyeMsink.connect("format-location-full", self.format_location_full_callback_eye)
        self.appScenesink.set_property('location',  self.path+'/scene-'+self.ExpNamestring+self.timestr+"-%d.mov")
        self.appScenesink.connect("format-location-full", self.format_location_full_callback_scene)

        #Setting up the IMU, Gaze data and scene/eyes videos for processing and demonstration
        ########IMU#######################################
        self.appIMUsink.set_property("emit-signals", True)
        self.appIMUsink.connect("new-sample", self.IMU_new_buffer, self.appIMUsink)
        ########Gaze Data#################################
        self.appGazesink.set_property("emit-signals", True)
        self.appGazesink.connect("new-sample", self.Gaze_new_buffer, self.appGazesink)
        ########Eye Movie#################################
        self.appEyeMsinkGUI.set_property("emit-signals", True)
        self.appEyeMsinkGUI.connect("new-sample", self.EyeM_new_buffer, self.appEyeMsinkGUI)
        ########Scene Movie###############################
        self.appScenesinkGUI.set_property("emit-signals", True)
        self.appScenesinkGUI.connect("new-sample", self.SceneM_new_buffer, self.appScenesinkGUI)
        ########TTLs#######################################
        self.appTTLsink.set_property("emit-signals", True)
        self.appTTLsink.connect("new-sample", self.TTL_new_buffer, self.appTTLsink)

        # Set the destination of the saving files
        self.TobiiWriteThread.TobiiWriteWorker.setWriters(self.ExpNamestring, self.timestr, self.path)
        self.TobiiGazeWriteThread.TobiiGazeWriteWorker.setWriters(self.ExpNamestring, self.timestr, self.path)
        self.TobiiTSWriteThread.TobiiTSWriteWorker.setWriters(self.ExpNamestring, self.timestr, self.path)

        # Start playing
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("Unable to set the pextractIMUipeline to the playing state.")
            exit(-1)

        # Wait until error or EOS
        bus = self.pipeline.get_bus()

        # Parse the pipeline message
        while self.continue_run:
            #message = bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
            message = bus.timed_pop(10000)
            if message:
                if message.type == Gst.MessageType.ERROR:
                    err, debug = message.parse_error()
                    print(("Error received from element %s: %s" % (
                        message.src.get_name(), err)))
                    print(("Debugging information: %s" % debug))
                    break
                elif message.type == Gst.MessageType.EOS:
                    print("End-Of-Stream reached.")
                    break
                elif message.type == Gst.MessageType.STATE_CHANGED:
                    if isinstance(message.src, Gst.Pipeline):
                        old_state, new_state, pending_state = message.parse_state_changed()
                        print(("Pipeline state changed from %s to %s." %
                            (old_state.value_nick, new_state.value_nick)))
                elif message.type == Gst.MessageType.APPLICATION:
                    print(message.get_structure().get_name())

                
        print('End of streaming')
        self.Gstreamfinished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop
        self.pipeline.send_event(Gst.Event.new_eos())
        # Wait until the eos being processed
        time.sleep(5)
        # Set the pipeline state to NULL
        self.pipeline.set_state(Gst.State.NULL)

    def setInitName(self, namestr):
        if namestr:
            self.InitialNamestring = namestr
    def setExpName(self, namestr):
        if namestr:
            self.ExpNamestring = namestr

    # For extracting IMU data
    def extractIMU(self, streamString, IMUtime):
        Acc_ind = streamString.find("accelerometer")
        Mag_ind = streamString.find("magnetometer")

        if Acc_ind > 0:
            if self.continue_run:
                # print('g', self.continue_run)
                self.IMU_signal.emit('{"tacc":'+ str(IMUtime) + ',' +str(streamString[Acc_ind - 1:len(streamString) - 1])+'\n')

            #--- For extracting the variables use the following (i.e. AccD.acceletometer[0] -> x axis acceleration)
            #AccD = json.loads(streamString[Acc_ind - 2:len(streamString) - 1], object_hook=
            #lambda d: namedtuple('X', d.keys())
            #(*d.values()))

        if Mag_ind > 0 :
            if self.continue_run:
                # print('g', self.continue_run)
                self.IMU_signal.emit('{"tmag":'+ str(IMUtime) + ',' +str(streamString[Mag_ind - 1:len(streamString) - 1])+'\n')
            # --- For extracting the variables use the following (i.e. AccD.acceletometer[0] -> x axis acceleration)
            #MagD = json.loads(streamString[Mag_ind-2:len(streamString)-1], object_hook =
            #      lambda d : namedtuple('X', d.keys())
            #      (*d.values()))

    # For extracting Gaze data
    def extractGazeD(self, streamString, IMUtime):
        gaze2Dind = streamString.find("gaze2d")
        # Check if the JSON has gaze data
        if gaze2Dind > 0:
            # --- For extracting the gaze variables use the following (i.e. GazeD.gaze2d[0] -> gaze horizontal position in scene frame)
            #GazeD = json.loads(streamString[gaze2Dind - 2:len(streamString) - 1], object_hook=
            #lambda d: namedtuple('X', d.keys())
            #(*d.values()))

            if self.continue_run:
                # print('g', self.continue_run)
                self.Gaze_signal.emit('{"tgz":'+ str(IMUtime) + ',' +str(streamString[gaze2Dind - 1:len(streamString) - 1])+'\n')

    # For sending eye video timestamps
    def extractTS_eye(self, time):
        if self.continue_run:
            self.TS_signal.emit('{"ttseye":'+ str(time) + '}'+'\n')
            self.elapsedTime = time;

    # For sending scene video timestamps
    def extractTS_scene(self, time):
        if self.continue_run:
            self.TS_signal.emit('{"ttsscene":'+ str(time) + '}'+'\n')

    # For sending scene video timestamps
    def extractTTL(self, streamString, IMUtime):
        TTLind = streamString.find("direction")
        if TTLind > 0:
            if self.continue_run:
                print('T')
                self.TTL_signal.emit('{"tttl":'+ str(IMUtime) + ',' +str(streamString[TTLind - 1:len(streamString) - 1])+'\n')

    def EstablishKeyworkEvents(self, events):
        if self.continue_run:
            self.TTL_signal.emit('{"tevent":' + str(self.elapsedTime) + ',"KeyEvents":' + '"'+ str(events) + '"' + '}\n')