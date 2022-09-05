# Modular Streaming Pipeline of Eye/Head Tracking Data Using Tobii Pro Glasses 3
This repository accompanies the [paper](https://www.biorxiv.org/content/10.1101/2022.09.02.506255v1) on open-source python library for real-time collection and analysis of eye/head Tracking data.   

Write the following in the terminal to start streaming. 
```
python3 TP3Py_main.py
```

## Ubuntu Installation
Installing Gstreamer, Opencv, and pyqt5: 
```
sudo apt install libgstreamer1.0-0 gstreamer1.0-plugins-{base,good,bad,ugly} gstreamer1.0-tools python3-gi gir1.2-gstreamer-1.0  gstreamer1.0-libav python3-pip libopencv-dev python3-opencv python3-pyqt5 qtcreator pyqt5-dev-tools qttools5-dev-tools qt5-default qt5ct

python3 -m pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
```
## Windows Installation 
We will have to build an environemt where gstreamer libraries can be installed properly. For this reason install [MySys2](https://www.msys2.org/) application and open the mingw 64bit terminal. 
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

## Contact and information 
Please keep us posted on issues. 

## License
Copyright [2022] [SUNYOpt]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


