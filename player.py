import gi
import sys
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib


# Player initialization and backend methods
class Player:

    def __init__(self):
        Gst.init(None)

        # custom playbin pipeline
        self.playbin = Gst.parse_launch("playbin")

        if not self.playbin:
            sys.stderr.write("'playbin' gstreamer plugin missing\n")
            sys.exit(1)
        self.playbin.set_state(Gst.State.READY)
        self.status = Gst.State.READY
        
        self.bus = self.playbin.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.bus_call)

       
        # This are only used in the command line and not for gtk app
        self.playlist = []
        self.currentIndex = 0
        self.current = None
        self.loop = GLib.MainLoop()


    def cust_func(self):
        #  Custom function can be redefined to run in bus_call during playback
        #  So that next song will play automatically when end of stream
        pass


    # This is used to check the status of the file being played
    def bus_call(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            sys.stdout.write("End-of-stream\n")
            self.changeState(Gst.State.NULL)

            self.cust_func()
        
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error While Playing: ", err)
            self.changeState(Gst.State.NULL)
        
            self.cust_func()


    def setUri(self, uri):
        self.changeState(Gst.State.NULL)
        self.playbin.set_property("uri", uri)
        self.current = uri

    def play(self):
        self.changeState(Gst.State.PLAYING)

    def pause(self):
        self.changeState(Gst.State.PAUSED)

    def stop(self):
        self.changeState(Gst.State.NULL)

    def changeState(self, state):
        self.playbin.set_state(state)
        self.status = state

    def getVolume(self):
        return self.playbin.get_property("volume")

    def setVolume(self, vol):
        # mapping vol from 0-1.0 to 0-10.0 but not required as audio will not be clear
        # vol = (vol)/(1.0)*(10.0)
        self.playbin.set_property("volume", vol)


    def getDuration(self):
        return self.playbin.query_duration(Gst.Format.TIME)

    def getPosition(self):
        return self.playbin.query_position(Gst.Format.TIME)

    def seek(self, location):
        self.playbin.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, location * Gst.SECOND)

    def validateUri(self, uri):
        return Gst.uri_is_valid(uri)


# Cli methods only called in cli mode
    def cliPlay(self):

        if(self.currentIndex >= len(self.playlist)):
            self.loop.quit()
            return

        uri = Gst.filename_to_uri(self.playlist[self.currentIndex])
        if(self.validateUri(uri)):
            self.setUri(uri)
            print("Now Playing:", self.playlist[self.currentIndex])
            self.play()
            self.currentIndex += 1
            if not self.loop.is_running():
                self.loop.run()
        else:
            print("Invalid URI Playing next: ")
            self.cliPlay()

   

# CLI version

def main(args):
    player = Player()
    player.cust_func = player.cliPlay  # This is done to play the next song automatically when end-of-stream
    try:
        player.playlist = args[1:]
        if(len(player.playlist) == 0):
            raise Exception("usage: %s <media file or uri>" % args[0])
        else:
            player.cliPlay()  # loop runs here and ends when playing is done
            raise Exception("End of Playlist")
    except Exception as e:
        print(e)
        sys.exit(0)



if __name__ == '__main__':
    sys.exit(main(sys.argv))



