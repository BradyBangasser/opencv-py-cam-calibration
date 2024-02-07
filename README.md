# opencv-py-cam-calibration

A simple Python program to calibrate cameras

# Usage 

You will need to print off a Charuco Board for the camera to calibrate, you can do that by running 
```bash
python3 ./calibration.py -n
```

You can then run to start the calibration, you will need to take 30 pictures of the board with your camera by pressing the space key
```bash
python3 ./calibration.py
```

# Advanced Usage

```bash
python3 ./calibration.py [opts]
```

# -u
Use preexisting images in the calibration-imgs directory 

# -f
Force

# -n 
Create a new CharcoBoard

# -s [i]
Specify camera source index
