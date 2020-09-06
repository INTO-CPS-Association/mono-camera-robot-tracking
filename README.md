# Mono Camera Robot Tracking

## Project Description
The purpose of this project is to give a tool for robot tracking which is simple to setup and easy to bring along. Examples of use can be in demos for conferences, light weight is prefered for traveling purposes and a simple setup is wanted in a already stressing new environment.
The technology uses just a single camera to track as many robots as wanted. The camera can be placed everywhere and does not need a fixed location, nor does it need to be placed at a known height, angle to the ground, or viewing-angle of the track. 
It is as easy as:
1. setup camera at random
2. Point camera at the track
3. Connect camera to the computer
4. Start program.

**Notice:** Read *Setup Hardware* to see what is needed beforehand for the camera to track the robots.

### Uses Circles for the tracking
The reason only a single camera is needed and can be places randomly is because other objecs is used this information's stead.
What is used is circles. These circles is split up into two categories:
* Calibration Circles
* Robot Circles

The two kind of circles look the same but are seperated by the ID on them (Number of smaller circles inside).
Examples of circles can here be seen, with the id of 3, 5, and 7 correspondingly. 
![Circle IDs](Images/circle_ids.png)

*OBS!: Where the smaller circles is placed does not matter.*


**Calibration Circles**

The Calibration Circles is used to calibrate the camera. These circles' coordinates must be fixed thoughout the duration of the program - Each circle's coordinate and size must be accessible for the program (See "Setup Software").
It must be possible for the camera to see at least three Calibration Circles for it to calibrate. As long as this is met will the camera be able to find its own coordinates, height, angle, and viewpoint. An image with three Calibration Circles places on the ground can be seen after this section. The circles can be further apart or closer to each other, depending on the enviroment, the only requirement is that they are not placed on a slope.

![Calibration Circles](Images/calibration_circles.png)

*OBS!: It is only when calibrating that the Calibration Circles must be visible. The circles can be hidden by e.g. the robots afterwards.*


**Robot Circles**

The Robot Circles is used to track the robots. The camera must be able to see at least three circles on a single robot before tracking is possible. The circles can with advantage be placed on each side of a robot to maximize the likelihood of the camera seeing three of them. Each circle's placement on the robot and its size must be accessible for the program (See "Setup Software).



### Images of the project

Image of the setup with the camera pointing at a track with a robot on it:
![Physical setup](/Images/physical_setup.png)

Image of the track seen from the camera together with the detected coordinates written to a terminal:
![Robot tracking](/Images/robot_tracking.png)

Image of the circles being tracked in the image:
![Ellipse tracking](/Images/circle_tracking.png)



## Setup Hardware
One of the following cameras-types is required for setting up the Hardware:
1. USB Camera
2. HDMI Camera

The USB Camera can be connected directly to the PC and does not require extra equipment.

The HDMI Camera probably needs the following part:
* HDMI-To-HDMI or MicroHDMI-To-HDMI 
* HDMI-To-USB converter

The extra converters for the HDMI Camera is required because a computer's HDMI-port only is an output and cannot take a HDMI-signal in from the camera. The HDMI signal needs, therefore, to be converted to an USB-signal which the PC can take as an input signal.

*OBS!: Higher resolution means better tracking BUT slower performance*
*OBS!: Multiple cameras can be connected to the program in case the track is too large.*


## Setup Software


### Language and dependencies
This project uses **Python 3.6** or higher. The following libraries is used in the project and must be installed for python befor use:
* Random (default)
* Operator (default)
* Time (default)
* Math (default)
* Copy (default)
* scikit-learn
* Scikit-image
* Numpy
* Opencv-python

*Hint: Use pip to install the libraries + the ones with (default) does not need to be installed* 



### Can't find the cameras information?



## Example



## Personalize extensions




