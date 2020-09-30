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


        # search for the widget with id
        # main window
        window = builder.get_object("window")
        # buttons
        self.playBtn = builder.get_object("playBtn")
        chooserBtn = builder.get_object("chooserBtn")

        # playlist
        self.playlistBox = builder.get_object("playlist")

        # headerbar
        self.headerBar = builder.get_object("headerBar")


        # slider seeker
        self.seeker = builder.get_object("seeker")
        self.durationText = builder.get_object("duration")


        # icons
        self.playIco = builder.get_object("playIco")
        self.pauseIco = builder.get_object("pauseIco")


        # UI 
        window.set_title("Python Gtk Player")
        
        # Connect Signals Here
        # window signals
        window.connect("destroy", self.onDestroy)
        # button signals
        self.playBtn.connect("clicked", self.onPlay)

        chooserBtn.connect("clicked", self.onChooseClick)

        self.playlistBox.connect("row-activated", self.onSelectionChange)

        self.sliderHandlerId = self.seeker.connect("value-changed", self.onSliderSeek)
        
        # misc

        # show window and initialize player gui
        window.show()
        Gtk.main()

    # Used to add items in Playlist View
    def refreshPlaylist(self, playlist, listBox):
        for location in playlist:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(spacing=50)
            # This should not be used
            setattr(row, "path", location)
            setattr(row, "name", Path(location).name)
            row.add(hbox)
            label = Gtk.Label(label=Path(location).name)
            hbox.pack_start(label, False, False, 1)
            listBox.add(row)
        listBox.show_all()


    def refreshIcons(self):
        # if song is paused show play icon and vice versa
        if(self.player.status == Gst.State.PAUSED):
            self.playBtn.set_image(self.playIco)
            self.playBtn.set_label("Play")
        elif(self.player.status == Gst.State.PLAYING):
            self.playBtn.set_label("Pause")
            self.playBtn.set_image(self.pauseIco)

    def refreshSlider(self):
        
        if self.player.status != Gst.State.PLAYING:
            return False  # cancel timeout
        else:
            success, duration = self.player.playbin.query_duration(Gst.Format.TIME)
            if not success:
                print("Error Occured")
                return False
            else:
                self.seeker.set_range(0, duration / Gst.SECOND)
            #fetching the position, in nanosecs
            success, position = self.player.playbin.query_position(Gst.Format.TIME)
            
            if not success:
                print("Couldn't fetch current song position to update slider")
                return False
                            
            # converts to seconds
            d = float(duration) / Gst.SECOND
            p = float(position) / Gst.SECOND

            durationToShow = str(time.strftime("%M:%S", time.gmtime(d)))
            postionToShow = str(time.strftime("%M:%S", time.gmtime(p)))
            self.durationText.set_label(postionToShow+"/"+durationToShow)

            # block seek handler so we don't seek when we set_value() or else audio will break 
            self.seeker.handler_block(self.sliderHandlerId)
            self.seeker.set_value(p)
            self.seeker.handler_unblock(self.sliderHandlerId)
                    
            return True  # continue calling every SLIDER_REFRESH milliseconds


    # Handle Signals Here
    def onDestroy(self, *args):
        Gtk.main_quit()
        
    def onPlay(self, button):
        # button is same as self.playBtn
        if not self.playlistBox.get_selected_row():
            print("Select a Song First")
        elif(self.player.status != Gst.State.PLAYING):
            self.player.play()
            GLib.timeout_add(SLIDER_REFRESH, self.refreshSlider)
        else:
            self.player.pause()
        self.refreshIcons()



    def onChooseClick(self, window):
        choose = FileChooser()
        self.refreshPlaylist(choose.selected, self.playlistBox)    


    def onSelectionChange(self, listbox, row):
        # Should not be used
        selected_song = getattr(row, "path")
        name = getattr(row, "name")
        rowBox = row.get_child()
        selected_song = Gst.filename_to_uri(selected_song)
        self.player.setUri(selected_song)
        self.headerBar.set_title(name)
        self.onPlay(button=None)
        
    def onSliderSeek(self, slider):
        self.player.seek(self.seeker.get_value())


def main(args):
    PlayerUI()

if __name__ == '__main__':
    sys.exit(main(sys.argv))


