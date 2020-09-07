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
**One** of the following cameras-types can be used when setting up the Hardware:
1. USB Camera
2. HDMI Camera

The USB Camera can be connected directly to the PC and does not require extra equipment.

The HDMI Camera probably needs the following part:
* HDMI-To-HDMI or MicroHDMI-To-HDMI 
* HDMI-To-USB converter

The extra converters for the HDMI Camera is required because a computer's HDMI-port only is an output and cannot take a HDMI-signal in from the camera. The HDMI signal needs, therefore, to be converted to an USB-signal which the PC can take as an input signal.

*OBS!: Higher resolution means better tracking BUT slower performance. Larger circles means better tracking as well*

*OBS!: Multiple cameras can be connected to the program in case the track is too large.*


## Setup Software


### Language and dependencies
This project uses **Python 3.6** or higher. The following libraries is used in the project and must be installed for python befor use:
* Random (default)
* Operator (default)
* Time (default)
* Math (default)
* Copy (default)
* Scikit-learn
* Scikit-image
* Numpy
* Opencv-python

*Hint: Use Pip to install the libraries + the ones with (default) does not need to be installed* 


### Can't find the camera's information?
Can't find the required camera information on the internet? No problem! The information can be found manually with a bit of work. A help function is avaiable in the program to make this manual setup easier.

The function can be found in "*ExtraHelpTools.py*" as the class "*CameraInformationHelpTool*". There is two functions in this class that can be used to find the information nessesary for calibrating the camera:
* get_viewing_angle_height(object_height, length_from_camera)
* get_viewing_angle_width(object_width, langth_from_camera)

This is how the functions is used:
1. Decide on a viewing angle you want to find (height in this example)
2. Find a object (e.g. a piece of paper) and measure its height
3. Start the camera you want to find the information for (NOT with the program, but just to see what it sees)
4. Move the object you chose closer/farther to/from the camera until the top and bottom of the object hits the top and bottom of the image frame
    * See the two images under these step to see an example of this
5. Measure the length from the camera when *step 4* is met
6. Plot the measured height and measured length from camera into the function. It will return the viewing angle used for the camera information
    * In this case 'view_degrees_vertical'

Example code:

```python
view_degree_vertical = CameraInformationHelpTool.get_viewing_angle_height(201, 550)
camera_prob = { 'view_degrees_vertical': view_degree_vertical }
camera_info = CameraInfo(address = 0, internal_properties = camera_prob)
```

The object in the image frame:
![Camera setup - In frame](/Images/object_in_frame.png)

The object in the image aligning with the to top and bottom of the frame:
![Camera setup - Align with frame](/Images/object_aligning_with_frame.png)



### Focus
The focus will automatically be calibrated if nothing else has been defined in the camera properties. This auto-focus will take a bit of time each time the program starts and does not guarantee the best focus. The focus can also be manually set if a faster upstart time or better calibration is wanted. The auto and manual way of calibrating the focus can be seen in the following two code snippets. 

Auto Calibration:
```python
camera_prob = { 'view_degrees_vertical': view_degree_vertical,
                'focus': None }
camera_info = CameraInfo(address = 0, internal_properties = camera_prob)
```

The focus will per default be set to 'None', this example is to show that the Auto calibration is done when the focus parameter has not been set.

Manual Calibration:
```python
camera_prob = { 'view_degrees_vertical': view_degree_vertical,
                'focus': 150 }
camera_info = CameraInfo(address = 0, internal_properties = camera_prob)
```

The focus have in this example been set to 150. The focus value can be every integer between *0 and 255*.


## Example Program
An example file is available to show how the project can be set up and used in a small program. The program prints the robots' position to the terminal.

The example can be found in the file "Example.py". The code will be explained here to give an insight into how it works. The explaination starts from the top and moved down.

**Explanation of the Example program**



## Personalize extensions




