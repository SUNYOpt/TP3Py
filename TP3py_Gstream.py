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
import datetime


from gi.repository import Gst, GstApp, GLib
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

Gst.init(None)


class TP3py_Gstream(QObject):
    
    """Set of signals for outputting the data being streamed to other threads"""   
    # give worker class a finished signal
    Gstreamfinished = pyqtSignal() 
    EyeVideo_signal = pyqtSignal(numpy.ndarray)
    SceneVideo_signal = pyqtSignal(numpy.ndarray)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class
        
        self.pipeline = Gst.parse_launch('videotestsrc  is-live=true !  video/x-raw,format= I420,framerate=50/1 ,width=1024,height=256 ! \
        videoconvert ! appsink name= Appeyesink  \
        videotestsrc  is-live=true !  video/x-raw,format= I420,framerate=50/1 ,width=1024,height=256 ! \
        videoconvert ! appsink name= Appscenesink  ')

        self.appEyeMsinkGUI = self.pipeline.get_by_name("Appeyesink")
        self.appScenesink = self.pipeline.get_by_name("Appscenesink")

        print("Gstream init. done!")


    #emitting the video buffer in change_pixmap_signal
    def gst_to_eyeimage(self, sample):
        buf = sample.get_buffer()
        recievedTime = (buf.pts)/1e9 
        caps = sample.get_caps()
        
        #print(caps.get_structure(0).get_value('format'))
        #print(caps.get_structure(0).get_value('height'))
        #print(caps.get_structure(0).get_value('width'))
        #print(buf.get_size())


        arr = numpy.ndarray(
            (caps.get_structure(0).get_value('height'),
             caps.get_structure(0).get_value('width'),
             1),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=numpy.uint8)

        self.EyeVideo_signal.emit(arr)
        return arr, recievedTime



    def EyeM_new_buffer(self, sink, data):
        sample = sink.emit("pull-sample")
        EyeImageBuffer, IMUtime = self.gst_to_eyeimage(sample)

        return Gst.FlowReturn.OK

    def do_work(self):
        global namestring
        #print(datetime.date(datetime.datetime.now()))

        #Inputting the saving path and the file name

        #Setting the buffer handler of appEyeMsinkGUI
        self.appEyeMsinkGUI.set_property("emit-signals", True)
        self.appEyeMsinkGUI.connect("new-sample", self.EyeM_new_buffer, self.appEyeMsinkGUI)
        


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

