# PyGObject Player

## Requirements for running in Windows

1. Go to http://www.msys2.org/ and download the x86_64 installer
2. Follow the instructions on the page for setting up the basic environment
3. Run C:\msys64\mingw64.exe - a terminal window should pop up
4. Execute `pacman -Suy`
5. Execute `pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-gstreamer mingw-w64-x86_64-gstreamer-plugins-good`
6. Execute `python main.py` for GUI or `python player.py <paths to media as arguments>` for command line 

---

I have not tested it on linux but the packages described above should be installed (without the `mingw-w64-x86_64-` part) using the package manager and it should probably work.

