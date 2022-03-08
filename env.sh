#!/bin/bash

sudo apt-get update

# For wxPython env
sudo apt-get install dpkg-dev build-essential python3-dev freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libjpeg-dev libnotify-dev libpng-dev libsdl2-dev libsm-dev libtiff-dev libwebkit2gtk-4.0-dev libxtst-dev
## For GTK2
#sudo apt-get install libgtk2.0-dev libwebkitgtk-dev

sudo pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04/ wxPython
#sudo pip3 install wxPython==4.0.0b2
sudo pip3 install PyPubSub==4.0.3
#sudo pip3 install opencv-python
sudo pip3 install opencv-contrib-python

## For python env
#sudo apt-get install build-essential openssl libssl-dev libffi-dev zlib1g-dev
sudo apt-get install upx
sudo pip3 install pyinstaller
sudo chmod -R 777 "./"

