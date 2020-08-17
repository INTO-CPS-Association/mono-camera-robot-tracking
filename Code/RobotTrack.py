import cv2
import numpy as np
import copy


from IdentifyCircleDistance import IdentifyCircleDistance
from IdentifyCircleRotation import IdentifyCircleRotation



class RobotTrack:
    def __init__(self):
        pass

    def run_robot_track(self, image, cirle):
        circle['distance'] = IdentifyCircleDistance().calculate_distance_to_circle(image, circle)
        circle['rotation'] = IdentifyCircleRotation().calculate_circle_rotation(image, circle)
