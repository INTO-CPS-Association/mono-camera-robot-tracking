from RobotResources import RobotResources, CircleResources
from Models.EllipseModels import Ellipse, RobotEllipse

import copy
import numpy as np
import math
from numpy import sqrt, dot, cross
from numpy.linalg import norm



class CameraCalibration:
    def __init__(self):
        pass

    def calibration(camera, robot_ellipses, circle_resources):
        if len(robot_ellipses) < 3:
            raise Exception("There needs to be a minimum of 3 ellipses")

        #Get the ellipses local coordinates
        coordinates = self._get_ellipse_coordinates(robot_ellipses, circle_resources)
        coordinate_ellipses = self._combine_ellipses_and_coordinates(robot_ellipses, coordinates)
        #calculate the camera's (x, y, z) coordinates
        camera_position = self._calculate_camera_position(coordinate_ellipses)
        camera.set_position(camera_position)
        #Calculate the camera's angle
        camera_angle = self._calculate_camera_angle(camera, coordinate_ellipses)
        camera.set_angle(camera_angle)
        #Calculate the camera's rotation abount z-axis
        camera_rotation = self._calculate_camera_rotation(camera, coordinate_ellipses)
        camera.set_angle(camera_rotation)

    def _get_ellipse_coordinates(self, ellipses, circle_resources):
        #Get coordinates for each ellipse by using the circle_resources
        return { ellipse.get_id(): {'coor': circle_resources.get_coordiante_by_id(ellipse.get_id())} for ellipse in ellipses}

    def _combine_ellipses_and_coordinates(self, ellipses, coordinates):
        return [{'ellipse': ellipse, 'coordinate': coordinates[ellipse.get_id()]} for ellipse in ellispes]

    def _calculate_camera_position(self, coordinate_ellipses):
        camera_height = self._calculate_camera_height(coordinate_ellipses)
        distances_to_camera = self._calculate_distances_to_camera(coordinate_ellipses)
        coor_dist_pairs = self._convert_to_coor_dist_pairs(coordinate_ellipses, distances_to_camera)
        x, y = self._calculate_circles_intersection(coor_dist_pairs)
        camera_position = (x, y, camera_height)
        return camera_position

    def _calculate_camera_height(self, coordinate_ellipses):
        height_list = []
        for coor_ellipse in coordinate_ellipses:
            distance = coor_ellipse['ellipse'].get_distance()
            angle = coor_ellipse['ellipse'].get_angle()
            height = math.sin(math.radians(angle)) * distance
            height_list.append(height)
        approx_height = sum(height_list) / len(height_list)
        return approx_height

    def _calculate_distances_to_camera_plane(self, coordinate_ellipses):
        dist_to_cam_dict = {}
        for coor_ellipse in coordinate_ellipses:
            ellipse = coor_ellipse['ellipse']
            distance = ellipse.get_distance()
            angle = ellipse.get_angle()
            plane_distance = math.cos(math.radians(angle)) * distance
            id = ellipse.get_id()
            dist_to_cam_dict[id] = plane_distance
        return dist_to_cam_dict

    def _convert_to_coor_dist_pairs(self, coordinate_ellipses, distances):
        coor_dist_pairs = []
        for coor_ellipse in coordinate_ellipses:
            coordinate = coor_ellipse['coordinate']
            ellispe = coor_ellipse['ellipse']
            plane_dist = distances[ellipse.get_id()]
            pair = {'coordinate': coordinate, 'distance': plane_dist}
            coord_dist_pairs.append(pair)
        return coor_dist_pairs

    def _calculate_circles_intersection(self, circles):
        intersection_list = []
        #Try to find intersection from each circle to avoid local maximum
        for circle in circles:
            coor, score = self._circles_edge_gradient_descent(circles, circle)
            intersection_list.append({'coordinate': coor, 'score': score})
        #Find minimum intersection
        min_intersection = intersection_list[0]
        for intersection in intersection_list:
            if intersection['score'] < min_intersection['score']:
                min_intersection = intersection
        return min_intersection

    def _circles_edge_gradient_descent(circles, start_circle):
        current_point = start_circle['coordinate']
        previous_point = None
        jump = 8
        minimum_jump = 1
        while previous_point != current_point and minimum_jump == 1:
            if previous_point == current_point:
                jump /= 2
            coor_error_list = self._calculate_gradiant_jump_errors(circles, current_point)
            coor_error = self._find_minimum_error(coor_error_list)
            previous_point = current_point
            current_point = coor_error['coordinate']
        return current_point, error

    def _calculate_gradiant_jump_errors(self, circles, starting_point, jump_size):
        coor_error_list = []
        coor_error_start = self._calculate_gradiant_jump_error(circles, (starting_point[0], starting_point[1]))
        coor_error_list.append(coor_error_start)
        coor_error_right = self._calculate_gradiant_jump_error(circles, (starting_point[0]+jump_size, starting_point[1]))
        coor_error_list.append(coor_error_right)
        coor_error_up = self._calculate_gradiant_jump_error(circles, (starting_point[0], starting_point[1]+jump_size))
        coor_error_list.append(coor_error_up)
        coor_error_left = self._calculate_gradiant_jump_error(circles, (starting_point[0]-jump_size, starting_point[1]))
        coor_error_list.append(coor_error_left)
        coor_error_down = self._calculate_gradiant_jump_error(circles, (starting_point[0], starting_point[1]-jump_size))
        coor_error_list.append(coor_error_down)
        return coor_error_list

    def _calculate_gradiant_jump_error(self, circles, coordinate):
        error_start = self.find_aggragated_intersection_error(circles, coordinate)
        coor_error = {'coordinate': coordinate, 'error':error_start}
        return coor_error

    def _find_aggregated_intersection_error(self, circles, coordinate):
        error = 0
        for circle in circles:
            circle_center = circle['center']
            circle_radius = circle['radius']
            angle_RAD = self._find_vector_angle(circle_center, coordinate)
            edge_coor = self._find_circle_edge_from_angle(angle_RAD, circle_radius)
            distance = math.sqrt((coordinate[0] - edge_coor[0])**2 + (coordinate[1] - edge_coor[1])**2)
            error += distance
        return dist

    def _find_vector_angle(self, point_a, point_b):
        vector = (point_b[0] - point_a[0], point_b[1] - point_a[1])
        length_vector = math.sqrt(vector[0]**2 + vector[1]**2)
        normalized_y = vector[1] / length_vector
        angle_RAD = math.asin(normalized_y)
        return angle_RAD

    def _find_circle_edge_from_angle(self, angle_RAD, radius):
        x = math.cos(angle_RAD) * radius
        y = math.sin(angle_RAD) * radius
        edge_point = (x, y)
        return edge_point

    def _find_minimum_error(self, error_coor_list):
        return min(error_coor_list, key=lambda coor_error:coor_error['error'])

    def _calculate_camera_angle(self, camera, coordinate_ellipses):
        image_shape = camera.get_size()
        ellipses = [coordinate_ellipse['ellipse'] for coordinate_ellipse in coordinate_ellipses]
        A, b = _fill_A_b_regression_matrix(ellipses, image_shape)
        result = _regression_result_matrix(A, b)
        center_angle = result[0] + result[1] * math.log(int(image_shape[0]/2))
        camera_angle = center_angle
        return camera_angle, result

    def _regression_result_matrix(self, A, b):
        A_t = np.matrix.transpose(A_numpy)
        inv = np.linalg.inv(A_t.dot(A_numpy))
        Ab = A_t.dot(b)
        result = inv.dot(Ab)
        return result

    def _fill_A_b_regression_matrix(self, ellipses, image_shape):
        A = []
        b = []
        bottom_center = (int(image_shape[1]/2), 0)
        for ellipse in ellipses:
            coordinate = ellipse.get_center()
            distance = ellipse.get_distance()
            rotation = ellipse.get_rotation()
            center_distance_px = math.sqrt((bottom_center[0] - coordinate[0])**2 + (bottom_center[1] - coordinate[1])**2)
            A.append([1, math.log(center_distance_px)])
            b.append(rotation)
        A_numpy = np.array(A)
        b_numpy = np.array(b)
        return A_numpy, b_numpy



    def _calculate_camera_rotation(self, camera, coordinate_ellipses):
        pass


















#Nothing
