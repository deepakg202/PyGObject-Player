import gi
import sys
gi.require_version("Gtk", "3.0")
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, GObject, Gst, GLib




# Player initialization and backend methods
class Player:

    def __init__(self):
        Gst.init(None)
        self.playbin = Gst.ElementFactory.make("playbin", None)
        
        # self is not required here maybe
        self.fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.playbin.set_property("video-sink", self.fakesink)
        
        if not self.playbin or not self.fakesink:
            sys.stderr.write("'playbin' or 'fakesink' gstreamer plugin missing\n")
            sys.exit(1)
        self.playbin.set_state(Gst.State.READY)
        self.status = Gst.State.READY


    def bus_call(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.playbin.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            self.playbin.set_state(Gst.State.NULL)
            err, debug = message.parse_error()

    def play(self, uri):
        self.playbin.set_property('uri', uri)
        # print(self.playbin.get_state())
        self.status = Gst.State.PLAYING
        self.playbin.set_state(Gst.State.PLAYING)    

    def pause(self):
        self.playbin.set_state(Gst.State.PAUSED)
        self.status = Gst.State.PAUSED


class PlayerUI:
    def __init__(self):
        # Use Glade Template 
        builder = Gtk.Builder()
        builder.add_from_file("template/player.glade")
        
        # Initialize Player Backend
        self.player = Player()
        

        # search for the widget with id
        # main window
        window = builder.get_object("window")
        # buttons
        playBtn = builder.get_object("playBtn")


        # icons
        self.playIco = builder.get_object("playIco")
        self.pauseIco = builder.get_object("pauseIco")


        # Connect Signals Here
        # window signals
        window.connect("destroy", self.onDestroy)
        # button signals
        playBtn.connect("clicked", self.onPlay)

        # show window and initialize player gui
        window.show()
        Gtk.main()        


    # Handle Signals Here
    def onDestroy(self, *args):
        Gtk.main_quit()
        
    def onPlay(self, button):
        if(self.player.status != Gst.State.PLAYING):
            self.player.play("file:///C:/Users/Deepak/Desktop/GitProjects/GUI/a.mp3")
            button.set_label("Pause")
            button.set_image(self.pauseIco)
        else:
            button.set_image(self.playIco)
            self.player.pause()
            button.set_label("Play")

        

    def onPause(self, button):
        pass


def main(args):
    PlayerUI()

if __name__ == '__main__':
    sys.exit(main(sys.argv))


