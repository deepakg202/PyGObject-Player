import gi
import sys
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib


# Player initialization and backend methods
class Player:

    def __init__(self):
        Gst.init(None)

        self.cli = False  # Used to differemtiate between gui and cli

        self.playbin = Gst.ElementFactory.make("playbin", "playbin")
        self.fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.playbin.set_property("video-sink", self.fakesink)
        if not self.playbin or not self.fakesink:
            sys.stderr.write("'playbin' or 'fakesink' gstreamer plugin missing\n")
            sys.exit(1)
        self.playbin.set_state(Gst.State.READY)
        self.status = Gst.State.READY
        self.current = None
        self.duration = 0

        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call)

        # This are only used in the command line and not for gtk app
        self.playlist = []
        self.currentIndex = 0
        self.loop = GLib.MainLoop()

    # This is used to check the status of the file being played
    def bus_call(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            sys.stdout.write("End-of-stream\n")
            self.changeState(Gst.State.NULL)
            # PLays next song in cli
            if(self.cli):
                self.cliPlay()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error While Playing: ", err)
            self.changeState(Gst.State.NULL)
            # plays next song in cli
            if(self.cli):
                self.cliPlay()

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

    def getDuration(self):
        success, self.duration = self.playbin.query_duration(Gst.Format.TIME)

    def prev(self):
        pass

    def seek(self, location):
        pass

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
    player.cli = True
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



