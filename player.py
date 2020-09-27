import gi
import sys
gi.require_version('Gst', '1.0')
from gi.repository import Gst


# Player initialization and backend methods
class Player:

    def __init__(self):
        Gst.init(None)
        self.playbin = Gst.ElementFactory.make("playbin", "playbin")
        
        # self is not required here maybe
        self.fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.playbin.set_property("video-sink", self.fakesink)
        
        if not self.playbin or not self.fakesink:
            sys.stderr.write("'playbin' or 'fakesink' gstreamer plugin missing\n")
            sys.exit(1)
        self.playbin.set_state(Gst.State.READY)
        self.status = Gst.State.READY
        self.current = None

        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call)


    # This is used to check the status of the file being played
    def bus_call(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            sys.stdout.write("End-of-stream\n")
            self.playbin.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error While PLaying: ", err)
            self.playbin.set_state(Gst.State.NULL)


    def setUri(self, uri):
        self.playbin.set_property("uri", uri)
        self.current = uri

    def play(self):
        self.playbin.set_state(Gst.State.PLAYING)    
        self.status = Gst.State.PLAYING

    def pause(self):
        self.playbin.set_state(Gst.State.PAUSED)
        self.status = Gst.State.PAUSED


    def stop(self):
        self.playbin.set_state(Gst.State.NULL)
        self.status = Gst.State.NULL





