# PyGObject Player

Install Python3 first

## Requirements for running in Windows

1. Go to http://www.msys2.org/ and download the x86_64 installer
2. Follow the instructions on the page for setting up the basic environment
3. Run C:\msys64\mingw64.exe - a terminal window should pop up
4. Execute `pacman -Suy`
5. Execute `pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-gstreamer mingw-w64-x86_64-gstreamer-plugins-good`
6. Execute `python main.py` for GUI or `python player.py <paths to media as arguments>` for command line 

---

## Requirements for running in Linux (Tested in Debian)
1. Open terminal and execute `sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0`
2. Execute `sudo apt install python3-gst-1.0`
3. Execute `sudo apt install gstreamer1.0-gtk3 gstreamer1.0-plugins-good`
4. Execute `python3 main.py` for GUI or `python3 player.py <paths to media as arguments>` for command line 

