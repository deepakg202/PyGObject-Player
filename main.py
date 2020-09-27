import gi
import sys
gi.require_version("Gtk", "3.0")
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst
from pathlib import Path

from player import Player
# Python templates
from template.fileChooser import FileChooser


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

        # icons
        self.playIco = builder.get_object("playIco")
        self.pauseIco = builder.get_object("pauseIco")

        # Connect Signals Here
        # window signals
        window.connect("destroy", self.onDestroy)
        # button signals
        self.playBtn.connect("clicked", self.onPlay)

        chooserBtn.connect("clicked", self.onChooseClick)

        self.playlistBox.connect("row-activated", self.onSelectionChange)


        # misc

        # show window and initialize player gui
        window.show()
        Gtk.main()

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

    # Handle Signals Here
    def onDestroy(self, *args):
        Gtk.main_quit()
        
    def onPlay(self, button):
        # button is same as self.playBtn
        if not self.playlistBox.get_selected_row():
            print("Select a Song First")
        elif(self.player.status != Gst.State.PLAYING):
            self.player.play()
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
        print(rowBox)
        print(rowBox.get_center_widget())
        selected_song = Gst.filename_to_uri(selected_song)
        if(self.player.current != selected_song):
            self.player.stop()
            self.player.setUri(selected_song)
            self.player.play()
            self.headerBar.set_title(name)
        self.refreshIcons()


def main(args):
    PlayerUI()

if __name__ == '__main__':
    sys.exit(main(sys.argv))


