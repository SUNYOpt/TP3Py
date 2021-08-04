# For now a work around using test video capabilities of Gstreamer

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstApp", "1.0")
# importing the module
import json
from collections import namedtuple
import matplotlib.animation as animation
import sys
import os
import cv2
import numpy
from datetime  import datetime


from gi.repository import Gst, GstApp, GLib
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

Gst.init(None)


class TP3py_Gstream(QObject):
    
    """Set of signals for outputting the data being streamed to other threads"""   
    # give worker class a finished signal
    Gstreamfinished = pyqtSignal() 
    EyeVideo_signal = pyqtSignal(numpy.ndarray)
    SceneVideo_signal = pyqtSignal(numpy.ndarray)
    IMU_signal = pyqtSignal(str)
    Gaze_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class
        
        self.namestring = ""
        parent_dir = "C:/Users/user2999/Desktop/TobiiData"
        # Path
        self.path = os.path.join(parent_dir, datetime.today().strftime('%Y%m%d%H%M'))  
        self.timestr = datetime.today().strftime('-%H-%M')
        # Create the directory
        try: 
            os.mkdir(self.path) 
        except OSError as error: 
            print(error)  


        self.pipeline = Gst.parse_launch('rtspsrc location=rtsp://192.168.75.51:8554/live/all?gaze-overlay=true \
        latency=100 name=src protocols=GST_RTSP_LOWER_TRANS_TCP enable-meta=true do-timestamp=true  \
        src. ! application/x-rtp,payload=96 !  rtph264depay ! h264parse  ! tee name=tscene \
        tscene. ! queue ! avdec_h264 ! appsink name=Appscenesink \
        tscene. ! queue ! splitmuxsink  max-size-time=60000000000  name=scenesink \
        src. ! application/x-rtp,payload=98 !  rtph264depay ! h264parse  ! tee name=teye \
        teye. ! queue ! avdec_h264 ! videoscale ! video/x-raw,width=512, height=128! appsink name=Appeyesink\
        teye. ! queue ! splitmuxsink  max-size-time=60000000000  name=eyesink \
        src. ! application/x-rtp,payload=99 ! appsink name=Gazesink \
        src. ! application/x-rtp,payload=101 ! appsink name=IMUsink ')

        self.appEyeMsink = self.pipeline.get_by_name("eyesink")
        self.appIMUsink = self.pipeline.get_by_name("IMUsink")
        self.appGazesink = self.pipeline.get_by_name("Gazesink")
        self.appEyeMsinkGUI = self.pipeline.get_by_name("Appeyesink")
        self.appScenesinkGUI = self.pipeline.get_by_name("Appscenesink")
        self.appScenesink = self.pipeline.get_by_name("scenesink")


        print("Gstream init. done!")


    def format_location_full_callback (self, splitmux, fragment_id, firstsample):  
        #date = str(round(time.time() * 1000))  # take the timestamp
        #name = str(date)
        #print(name)
        #return int(name)
        buf =firstsample.get_buffer()
        print('Eye video pts: ',buf.pts)

    """ Scene movie buffer management """
    #Emitting the video buffer in SceneVideo_signal
    def gst_to_sceneimage(self, sample):
        buf = sample.get_buffer()
        recievedTime = (buf.pts)/1e9 
        caps = sample.get_caps()

        #print(caps.get_structure(0).get_value('height'))
        #print(caps.get_structure(0).get_value('width'))
        #print(buf.get_size())
        temph = caps.get_structure(0).get_value('height')//2
        tempw = caps.get_structure(0).get_value('width')//2
        size = temph*tempw 

        h = caps.get_structure(0).get_value('height')
        w = caps.get_structure(0).get_value('width')

        #print(size)
        YUV_arr = numpy.ndarray(
            (h*3//2, w),
            buffer=buf.extract_dup(0, h*w*3//2),
            dtype=numpy.uint8)

        """
        Y_arr = numpy.ndarray(
            (h, w),
            buffer=buf.extract_dup(0, h*w),
            dtype=numpy.uint8)

        Y_arr_resized = self.rebin(Y_arr,(temph,tempw))

        U_arr = numpy.ndarray(
            (temph, tempw),
            buffer=buf.extract_dup(h*w-1, size),
            dtype=numpy.uint8)

        V_arr = numpy.ndarray(
            (temph, tempw),
            buffer=buf.extract_dup(h*w-1+size, size),
            dtype=numpy.uint8)
        """
        #rTmp = Y_arr_resized + numpy.right_shift(351*(V_arr-128),8) 
        #rTmp = Y_arr_resized + (1.370705 * (V_arr-128))
        #gTmp = Y_arr_resized - (0.58 * (V_arr-128)) - (0.39 * (U_arr-128))
        #bTmp = Y_arr_resized + (2.03 * (U_arr-128))

        #rTmp = Y_arr_resized + (1.370705 * (V_arr-128))
        #gTmp = Y_arr_resized - (0.698001 * (V_arr-128)) - (0.337633 * (U_arr-128))
        #bTmp = Y_arr_resized + (1.732446 * (U_arr-128))

        #rTmp = rTmp.astype(numpy.uint8)
        #gTmp = gTmp.astype(numpy.uint8)
        #bTmp = bTmp.astype(numpy.uint8)     

        #rgbImg = numpy.stack([rTmp,gTmp,bTmp], axis=-1)

        #YUVImg = numpy.stack([Y_arr_resized,U_arr,V_arr], axis=-1)
        #print('Svne: ',YUV_arr.shape)
        self.SceneVideo_signal.emit(YUV_arr)
        return YUV_arr, recievedTime

    def rebin(self, arr, new_shape):
        shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
        return arr.reshape(shape).max(-1).max(1)

    def SceneM_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        EyeImageBuffer, IMUtime = self.gst_to_sceneimage(sample)

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
       
        #print('EyeI: ',arr.shape)

        self.EyeVideo_signal.emit(arr)
        return arr, recievedTime
    
    def EyeM_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        EyeImageBuffer, IMUtime = self.gst_to_eyeimage(sample)

        return Gst.FlowReturn.OK

    """ IMU buffer management """
    # Returns the raw output of IMU and Gaze Payloads
    def gst_to_IMU(self, sample):
        buf = sample.get_buffer()
        recievedTime = (buf.pts)/1e9 
        arr = numpy.ndarray(
            (1,buf.get_size()),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=numpy.uint8)
        
        
        return bytes(arr), recievedTime

    def IMU_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        streamString, IMUtime = self.gst_to_IMU(sample)
        self.IMU_signal.emit(str(streamString))
        
        #self.TobiiExtractor.extractIMU(str(streamString), IMUtime)
        return Gst.FlowReturn.OK

    """ Gaze data buffer management """
    # Returns the raw output of Gaze Payloads
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
        self.Gaze_signal.emit(str(streamString))
        
        #self.TobiiExtractor.extractIMU(str(streamString), IMUtime)
        return Gst.FlowReturn.OK



    def do_work(self):
        """
        Saving the scene and eye movies right away in a segmented manner while keeping the first frame timestamps
        """
        self.appEyeMsink.set_property('location',  self.path+'/eye-'+self.namestring+self.timestr+"-%d.mov")        
        self.appEyeMsink.connect("format-location-full", self.format_location_full_callback)       
        self.appScenesink.set_property('location',  self.path+'/scene-'+self.namestring+self.timestr+"-%d.mov")
        self.appScenesink.connect("format-location-full", self.format_location_full_callback)       

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


        # Start playing
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("Unable to set the pipeline to the playing state.")
            exit(-1)

        # Wait until error or EOS
        bus = self.pipeline.get_bus()

        # Parse message -- give the loop a stoppable condition
        while self.continue_run:
            message = bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
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
                    else:
                        print("Unexpected message received.")
            
        self.Gstreamfinished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop
        self.pipeline.send_event(Gst.Event.new_eos())
        #self.pipeline.set_state(Gst.State.NULL)

    def setExpName(self, namestr):
        self.namestring = namestr