# Coordinate calibration tool

### Introduction
This is a simple visualisation tool. It helps us to locate and transform coordinates, through videos and pictures.

### Environment
wxPython 4.0.0b2  
Pypubsub 4.0.3  
numpy 1.19.5  
opencv-python 4.6.0.66  

For questions related to the installation of wxPython, please refer to the official website:  
<https://github.com/wxWidgets/Phoenix>

### Modules
###### Main
```
├── config                       # Config folder
   └──  settings.ini             # General user parameter settings
├── data                         # Data folder
   └──  event_fusion.json        # Coordinate format file
├── icon                         # GUI icon folder
   └──  icon.png, ...            # Icons
├── images                       # Test image folder
   └──  test.png, ...            # Test images
├── videos                       # Test video folder
   └──  test.mp4, ...            # Test videos
├── run.py                       # Main program
├── panel_one.py                 # GUI first page
├── work_thread.py               # An thread for long-term tasks to avoid UI hang or crashes
├── thread_with_return_value.py  # Override python Thread class to get the return value
├── update_package.py            # Packing the data into a .tar file and transporting it via http post
```

###### Secondary
```
├── alarm_calibration            # Packed files folder
   ├── event_fusion.json         # Coordinate format file
   ├── info                      # Meta data
   ├── install.sh                # Install scripts for target devices
   └── uninstall.sh              # Uninstall scripts for target devices
├── _pyinstaller_build.py        # Packaged as an executive file
├── env.sh                       # Ubuntu 1804 environment installation scripts
```

###### Others
Just the test code.

### Effect
![preview](https://github.com/opababy/transfer_tool/github_data/preview.gif](https://github.com/opababy/transfer_tool/blob/main/github_data/preview.gif) "preview")

### To do
1. Update video mode.
2. Add live streaming mode.
