import numpy as np
import cv2, PIL
from cv2 import aruco
import pandas as pd
import math

from Models.EllipseModels import Ellipse, RobotEllipse
from Models.SquareModels import RobotSquare
from SpecialEllipses import SpecialEllipses


#-----------------------

class MarkerDetection:
    def __init__(self, marker_type = aruco.DICT_6X6_250):
        self._marker_type = marker_type
        self._marker_dict = aruco.Dictionary_get(self._marker_type)
        self.special_ellipses = SpecialEllipses(125)

    def get_markers(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        parameters =  aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, self._marker_dict, parameters=parameters)

        markers = []
        if ids is not None:
            for i in range(len(ids)):
                marker = {'id': 0, 'corners': [], 'size': 0, 'center': (0, 0)}
                c = corners[i][0]
                marker['id'] = ids[i][0]
                marker['corners'] = corners[i]
                marker['size'] = int(self._get_max_distance_between_points(c))
                marker['center'] = (int(c[:, 0].mean()), int(c[:, 1].mean()))
                markers.append(marker)
        return markers

    def _get_max_distance_between_points(self, points):
        max_distance = 0
        for first_index in range(len(points)):
            for second_index in range(first_index+1, len(points)):
                point_a = points[first_index]
                point_b = points[second_index]
                distance = math.sqrt((point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2)
                if distance > max_distance:
                    max_distance = distance
        return distance


    def get_robot_ellipses(self, cam, frame, markers):
        sub_frames = self._get_sub_frames(frame, markers)
        robot_ellipses = []
        for index, sub_frame in enumerate(sub_frames):
            ellipses = self._get_ellipses_in_frame(cam, sub_frame)
            ellipse = self._get_ellipse_in_ellipses(ellipses, sub_frame)
            norm_ellipse = self._normalize_ellipse(ellipse, markers, index)
            robot_ellipse = RobotEllipse(norm_ellipse, None, 0, 0, markers[index]['id'])
            robot_ellipses.append(robot_ellipse)
        return robot_ellipses

    def _get_sub_frames(self, frame, markers):
        sub_frames = []
        for marker in markers:
            center = marker['center']
            size = marker['size']
            starting_point = (center[0] - int(size * 1.5), center[1] - int(size * 1.5))
            ending_point = (center[0] + int(size * 1.5), center[1] + int(size * 1.5))

            if starting_point[0] < 0: starting_point = (0, ending_point[1])
            elif starting_point[0] >= frame.shape[1]: starting_point = (frame.shape[1] - 1, starting_point[1])
            if starting_point[1] < 0: starting_point = (starting_point[0], 0)
            elif starting_point[1] >= frame.shape[0]: starting_point = (starting_point[0], frame.shape[0] - 1)

            if ending_point[0] < 0: ending_point = (0, ending_point[1])
            elif ending_point[0] >= frame.shape[1]: ending_point = (frame.shape[1] - 1, ending_point[1])
            if ending_point[1] < 0: ending_point = (ending_point[0], 0)
            elif ending_point[1] >= frame.shape[0]: ending_point = (ending_point[0], frame.shape[0] - 1)

            sub_frame = frame[starting_point[1]:ending_point[1], starting_point[0]:ending_point[0]]
            sub_frames.append(sub_frame)
        return sub_frames

    def _get_ellipses_in_frame(self, cam, frame):
        ellipses = self.special_ellipses.get_raw_ellipses(cam, frame)
        return ellipses

    def _get_ellipse_in_ellipses(self, ellipses, frame):
        ellipse_error = { 'ellipse': ellipses[0], 'error': 100000 }
        frame_size = frame.shape
        for ellipse in ellipses:
            size_error = abs(ellipse.height()*2 - frame_size[0]) + abs(ellipse.width()*2 - frame_size[1])
            error = size_error
            if error < ellipse_error['error']:
                ellipse_error['ellipse'] = ellipse
                ellipse_error['error'] = error
        return ellipse_error['ellipse']

    def _normalize_ellipse(self, ellipse, markers, index):
        starting_point = (markers[index]['center'][0] - int(markers[index]['size'] * 1.5), markers[index]['center'][1] - int(markers[index]['size'] * 1.5))
        correct_center = (ellipse.center()[1] + starting_point[1], ellipse.center()[0] + starting_point[0])
        return Ellipse(ellipse.edge_pixels(), correct_center, ellipse.width(), ellipse.height(), ellipse.rotation())

    def get_robot_squares(self, markers):
        return [RobotSquare(marker) for marker in markers]

    def calc_rotation_translation_matrix(self, corners, marker_size, cam):
        camera_matrix = cam.get_cam_matrix()
        distortion_coefficients = cam.get_distortion_coeff()

        rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners, marker_size/100, camera_matrix, distortion_coefficients)
        return rvec, tvec













#Nothing
