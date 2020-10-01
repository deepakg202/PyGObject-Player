import gi
import sys
gi.require_version("Gtk", "3.0")
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GLib
from pathlib import Path

from player import Player
# Python templates
from template.fileChooser import FileChooser


import time

# This is the refresh time of slider in milliseconds
SLIDER_REFRESH = 1000

# Python templates

class PlayerUI:
    def __init__(self):
        # Use Glade Template 
        builder = Gtk.Builder()
        builder.add_from_file("template/player.glade")
        
        # Initialize Player Backend
        self.player = Player()
        self.player.cust_func = self.cust_func # Changing the custom function to use when media ends or reports error

        # search for the widget with id
        # main window
        window = builder.get_object("window")
        # buttons
        self.playBtn = builder.get_object("playBtn")
        chooserBtn = builder.get_object("chooserBtn")
        stopBtn = builder.get_object("stopBtn")
        nextBtn = builder.get_object("nextBtn")
        prevBtn = builder.get_object("prevBtn")
        
        # playlist
        self.playlistBox = builder.get_object("playlist")

        # headerbar
        self.headerBar = builder.get_object("headerBar")

        # PlayArea
        self.playArea = builder.get_object("playArea")

        # slider seeker
        self.seeker = builder.get_object("seeker")
        self.durationText = builder.get_object("duration")


        # icons
        self.playIco = builder.get_object("playIco")
        self.pauseIco = builder.get_object("pauseIco")


        # UI 
        window.set_title("PyGObject Player")
        

        # Connect Signals Here
        # window signals
        window.connect("destroy", self.onDestroy)
        # button signals
        self.playBtn.connect("clicked", self.onPlay)
        nextBtn.connect("clicked", self.onNext)
        prevBtn.connect("clicked", self.onPrev)
        stopBtn.connect("clicked", self.onStop)


        chooserBtn.connect("clicked", self.onChooseClick)

        self.playlistBox.connect("row-activated", self.onSelectionActivated)

        self.sliderHandlerId = self.seeker.connect("value-changed", self.onSliderSeek)
        
        self.playArea.connect("draw", self.onDraw)

        
        #  used for connecting video to application
        # self.player.bus.enable_sync_message_emission()
        # self.player.bus.connect("sync-message::element", self.onSyncMessage)


        # show window and initialize player gui
        window.show()
        Gtk.main()



    def onSyncMessage(self, bus, message):
        # print(dir(message))
        if message.get_structure() is None:
            return False



    def onDraw(self, area, ctx):
        pass


    # Used to select next or prev media 
    def cust_func(self, next=True): 
        playlist = self.playlistBox.get_children()
        currentIndex = playlist.index(self.playlistBox.get_selected_row())
        if(currentIndex >= len(playlist) - 1 or currentIndex == 0):
            print("End of PlayList")
            self.onStop()
            return
        else:
            if(next):
                currentIndex += 1
            else:
                currentIndex -= 1
        self.playlistBox.select_row(playlist[currentIndex])
        # calling the signal handler manually
        self.onSelectionActivated(self.playlistBox, playlist[currentIndex])


    # Used to add items in Playlist View
    def refreshPlaylist(self, playlist, listBox):
        for location in playlist:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(spacing=50)
            setattr(row, "path", location)
            setattr(row, "name", Path(location).name)
            row.add(hbox)
            label = Gtk.Label(label=Path(location).name)
            hbox.pack_start(label, False, False, 1)
            listBox.add(row)
        listBox.show_all()


    def refreshIcons(self):
        # if song is paused show play icon else play icon
        if(self.player.status == Gst.State.PLAYING):
            self.playBtn.set_label("Pause")
            self.playBtn.set_image(self.pauseIco)
        else:
            self.playBtn.set_image(self.playIco)
            self.playBtn.set_label("Play")
        

    def refreshSlider(self):  
        if self.player.status != Gst.State.PLAYING:
            return False  # cancel timeout
        else:
            
            try:
                success, duration = self.player.getDuration()
                d = float(duration) / Gst.SECOND
                if not success:
                    Exception("Error Occured when fetching duration")
                else:
                    self.seeker.set_range(0, d)
                #fetching the position, in nanosecs
                success, position = self.player.getPosition()
                
                if not success:
                    Exception("Couldn't fetch current song position to update slider")
                                
                # converts to seconds
                p = float(position) / Gst.SECOND

                durationToShow = str(time.strftime("%H:%M:%S", time.gmtime(d)))
                postionToShow = str(time.strftime("%H:%M:%S", time.gmtime(p)))
                self.durationText.set_label(postionToShow+"/"+durationToShow)

                # block seek handler so we don't seek when we set_value() or else audio will break
                self.seeker.handler_block(self.sliderHandlerId)
                self.seeker.set_value(p)
                self.seeker.handler_unblock(self.sliderHandlerId)
 
            except Exception as e:
                print(e)

            return True  # continue calling every SLIDER_REFRESH milliseconds

    
    # Handle Signals Here
    def onDestroy(self, *args):
        Gtk.main_quit()
        
    def onPlay(self, button=None):
        # button is same as self.playBtn
        if not self.playlistBox.get_selected_row():
            print("Select Songs First")
        elif(self.player.status != Gst.State.PLAYING):
            self.player.play()
            GLib.timeout_add(SLIDER_REFRESH, self.refreshSlider)
        else:
            self.player.pause()
        self.refreshIcons()

    def onChooseClick(self, window):
        choose = FileChooser()
        self.refreshPlaylist(choose.selected, self.playlistBox)    


    def onSelectionActivated(self, listbox, row): 
        selected_song = getattr(row, "path")
        name = getattr(row, "name")
        selected_song = Gst.filename_to_uri(selected_song)
        self.player.setUri(selected_song)
        self.headerBar.set_title(name)
        self.onPlay()
        
    def onSliderSeek(self, slider):
        self.player.seek(self.seeker.get_value())


    def onStop(self, button=None):
        self.player.changeState(Gst.State.NULL)
        self.seeker.set_value(0)
        self.refreshIcons()
    def onPrev(self, button=None):
        if not self.playlistBox.get_selected_row():
            print("Select Songs First")
        else:
            self.cust_func(next=False)
    def onNext(self, button=None):
        if not self.playlistBox.get_selected_row():
            print("Select Songs First")
        else:
            self.cust_func(next=True)


def main(args):
    PlayerUI()

if __name__ == '__main__':
    sys.exit(main(sys.argv))


