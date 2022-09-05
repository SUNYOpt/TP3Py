# Modular Streaming Pipeline of Eye/Head Tracking Data Using Tobii Pro Glasses 3
This repository accompanies the [paper](https://www.biorxiv.org/content/10.1101/2022.09.02.506255v1) on open-source python library for real-time collection and analysis of eye/head Tracking data.   


# Ubuntu Installation
Installing Gstreamer, Opencv, and pyqt5: 
```
sudo apt install libgstreamer1.0-0 gstreamer1.0-plugins-{base,good,bad,ugly} gstreamer1.0-tools python3-gi gir1.2-gstreamer-1.0  gstreamer1.0-libav python3-pip libopencv-dev python3-opencv python3-pyqt5 qtcreator pyqt5-dev-tools qttools5-dev-tools qt5-default qt5ct

python3 -m pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
```
# Windows Installation 
We will have to build an environemt where gstreamer libraries can be installed properly.

Install Install MySys2
Open mingw 64bit and write:
```
pacman -Syu 
```
Gstreamer installation:
```
pacman -S mingw-w64-x86_64-gstreamer mingw-w64-x86_64-gst-devtools mingw-w64-x86_64-gst-plugins-{base,good,bad,ugly} mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject
```
python:
```
pacman -S mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject
pacman -Sy mingw-w64-x86_64-python3-pip mingw-w64-x86_64-python3-numpy mingw-w64-x86_64-python3-scipy mingw-w64-x86_64-python3-matplotlib mingw-w64-x86_64-python3-pandas mingw-w64-x86_64-python3-Pillow
pacman -S mingw-w64-x86_64-python-matplotlib
pacman -S mingw-w64-x86_64-gst-rtsp-server
```
