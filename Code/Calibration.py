from Resources import RobotResources, CircleResources
from Models.EllipseModels import Ellipse, RobotEllipse

import copy
import numpy as np
import math
from numpy import sqrt, dot, cross
from numpy.linalg import norm



class CameraCalibration:
    def __init__(self):
        pass

    def calibrate(self, camera, robot_ellipses, circle_resources):
        if len(robot_ellipses) < 3:
            raise Exception("There needs to be a minimum of 3 ellipses")

        #Get the ellipses local coordinates
        coordinates = self._get_ellipse_coordinates(robot_ellipses, circle_resources)
        coordinate_ellipses = self._combine_ellipses_and_coordinates(robot_ellipses, coordinates)

        #calculate the camera's (x, y, z) coordinates
        camera_position = self._calculate_camera_position(coordinate_ellipses)
        camera.set_position(camera_position)

        print(camera_position)
        #Calculate the camera's angle
        camera_angle = self._calculate_camera_angle(camera, coordinate_ellipses, circle_resources)    #Hard to test? How to test?
        camera.set_angle_to_floor(camera_angle, 'rad')

        #Calculate the camera's rotation abount z-axis
        camera_rotation = self._calculate_camera_rotation(camera, coordinate_ellipses)
        camera.set_rotation_from_center(camera_rotation, 'rad')

        print("Angle: " + str(camera.get_angle_to_floor()))
        print("Rotation: " + str(camera.get_rotation_from_center()))


    def _get_ellipse_coordinates(self, ellipses, circle_resources):
        #Get coordinates for each ellipse by using the circle_resources
        return { ellipse.get_id(): {'coor': circle_resources.get_coordiante_by_id(ellipse.get_id())} for ellipse in ellipses}

    def _combine_ellipses_and_coordinates(self, ellipses, coordinates):
        return [{'ellipse': ellipse, 'coordinate': coordinates[ellipse.get_id()]} for ellipse in ellipses]

    def _calculate_camera_position(self, coordinate_ellipses):
        camera_height = self._calculate_camera_height(coordinate_ellipses)
        distances_to_camera = self._calculate_distances_to_camera_plane(coordinate_ellipses)
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
            coordinate = coor_ellipse['coordinate']['coor']
            ellipse = coor_ellipse['ellipse']
            plane_dist = distances[ellipse.get_id()]
            pair = {'coordinate': coordinate, 'distance': plane_dist}
            coor_dist_pairs.append(pair)
        return coor_dist_pairs

    def _calculate_circles_intersection(self, circles):
        intersection_list = []
        #Try to find intersection from each circle to avoid local maximum
        for circle in circles:
            coor, score = self._circles_edge_gradient_descent(circles, circle)
            intersection_list.append({'coordinate': coor, 'score': score})
        #Find minimum intersection
        min_intersection = self._find_min_intersection(intersection_list)
        return min_intersection['coordinate']

    def _find_min_intersection(self, intersection_list):
        min_intersection = intersection_list[0]
        for intersection in intersection_list:
            if intersection['score'] < min_intersection['score']:
                min_intersection = intersection
        return min_intersection

    def _circles_edge_gradient_descent(self, circles, start_circle):
        current_point = start_circle['coordinate']
        previous_point = None
        jump = 1024
        minimum_jump = 1
        while jump > minimum_jump or previous_point != current_point:
            if previous_point == current_point:
                jump = jump / 2
            coor_error_list = self._calculate_gradiant_jump_errors(circles, current_point, jump)
            coor_error = self._find_minimum_error(coor_error_list)
            previous_point = current_point
            current_point = coor_error['coordinate']
        return current_point, coor_error['error']

    def _calculate_gradiant_jump_errors(self, circles, starting_point, jump_size):
        coor_error_list = []
        coor = starting_point

        coor_error_start = self._calculate_gradiant_jump_error(circles, (coor[0], coor[1]))
        coor_error_list.append(coor_error_start)

        coor_error_0deg = self._calculate_gradiant_jump_error(circles, (coor[0]+jump_size, coor[1]))
        coor_error_list.append(coor_error_0deg)

        coor_error_45deg = self._calculate_gradiant_jump_error(circles, (coor[0]+jump_size, coor[1]+jump_size))
        coor_error_list.append(coor_error_45deg)

        coor_error_90deg = self._calculate_gradiant_jump_error(circles, (coor[0], coor[1]+jump_size))
        coor_error_list.append(coor_error_90deg)

        coor_error_135deg = self._calculate_gradiant_jump_error(circles, (coor[0]-jump_size, coor[1]+jump_size))
        coor_error_list.append(coor_error_135deg)

        coor_error_180deg = self._calculate_gradiant_jump_error(circles, (coor[0]-jump_size, coor[1]))
        coor_error_list.append(coor_error_180deg)

        coor_error_225deg = self._calculate_gradiant_jump_error(circles, (coor[0]-jump_size, coor[1]-jump_size))
        coor_error_list.append(coor_error_225deg)

        coor_error_270deg = self._calculate_gradiant_jump_error(circles, (coor[0], coor[1]-jump_size))
        coor_error_list.append(coor_error_270deg)

        coor_error_315deg = self._calculate_gradiant_jump_error(circles, (coor[0]+jump_size, coor[1]-jump_size))
        coor_error_list.append(coor_error_315deg)

        return coor_error_list

    def _calculate_gradiant_jump_error(self, circles, coordinate):
        error_start = self._find_aggregated_intersection_error(circles, coordinate)
        coor_error = {'coordinate': coordinate, 'error':error_start}
        return coor_error

    def _find_aggregated_intersection_error(self, circles, coordinate):
        error = 0
        for circle in circles:
            circle_center = self._circle_to_xy_coordinate(circle)
            circle_radius = circle['distance']
            distance_to_center = math.sqrt((coordinate[0] - circle_center[0])**2 + (coordinate[1] - circle_center[1])**2)
            distance_to_edge = abs(distance_to_center - circle_radius)
            error += distance_to_edge
        return error

    def _circle_to_xy_coordinate(self, circle):
        coordinate_3d = circle['coordinate']
        coordinate_2d = (coordinate_3d[0], coordinate_3d[1])
        return coordinate_2d

    def _find_vector_angle(self, point_a, point_b):
        if point_a == point_b:
            return 0
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

    def _calculate_camera_angle(self, camera, coordinate_ellipses, CircleResources):
        ellipse_1 = coordinate_ellipses[0]['ellipse']
        ellipse_2 = coordinate_ellipses[1]['ellipse']

        estimated_distance_1 = self._find_circle_distance_projected_into_image_center(camera, ellipse_1, CircleResources)
        estimated_distance_2 = self._find_circle_distance_projected_into_image_center(camera, ellipse_2, CircleResources)

        distance_1 = estimated_distance_1
        distance_2 = estimated_distance_2

        print("Distance1: " + str(distance_1))
        print("Height: "+ str(camera.get_position()[2]))
        print("Distance1: " + str(distance_2))

        v_1 = math.asin(camera.get_position()[2] / distance_1)
        v_2 = math.asin(camera.get_position()[2] / distance_2)

        p_1 = ellipse_1.get_center('y') / camera.get_frame_size('y')
        p_2 = ellipse_2.get_center('y') / camera.get_frame_size('y')

        v_diff = abs(v_1 - v_2)
        p_diff = abs(p_1 - p_2)

        v_0p = v_1 - ((v_diff/p_diff)*p_1)
        v_100p = v_2 + ((v_diff / p_diff)*(1-p_2))

        camera_angle = v_0p + abs(v_0p - v_100p) * 0.5
        return camera_angle

    def _find_circle_distance_projected_into_image_center(self, camera, ellipse, CircleResources):
        pixel_width_mm = CircleResources.get_size_by_id(ellipse.get_id()) / ellipse.get_width()
        circle_center_to_image_center_px = abs(ellipse.get_center()[0] - camera.get_frame_size('x'))
        circle_center_to_image_center_mm = circle_center_to_image_center_px * pixel_width_mm
        estimated_length = math.sqrt(ellipse.get_distance()**2 - circle_center_to_image_center_mm**2)
        return estimated_length


    def _calculate_camera_rotation(self, camera, coordinate_ellipses):
        camera_local_angle_to_ellipses = self._find_local_angle_between_camera_and_ellipses(camera, coordinate_ellipses)
        camera_global_angle_to_ellipses = self._find_global_angle_between_camera_and_ellipses(camera, coordinate_ellipses)

        real_angles = [camera_global_angle_to_ellipses[counter] - camera_local_angle_to_ellipses[counter] for counter in range(0, len(coordinate_ellipses))]
        rotation = sum(real_angles) / len(real_angles)
        return rotation


    def _find_local_angle_between_camera_and_ellipses(self, camera, coordinate_ellipses):
        angles = []
        for coordinate_ellipse in coordinate_ellipses:
            ellipse = coordinate_ellipse['ellipse']
            angle = self._find_angle_between_camera_and_pixel(camera, ellipse)
            angles.append(angle)
        return angles


    def _find_angle_between_camera_and_pixel(self, camera, ellipse):
        pixel = ellipse.get_center()
        d1 = ellipse.get_distance()

        X_p = pixel[0] / camera.get_frame_size('x')
        Y_p = pixel[1] / camera.get_frame_size('y')

        if X_p > 0.5:
            X_p = 1 - X_p
        if Y_p > 0.5:
            Y_p = 1 - Y_p

        v_HY = (camera.get_horizontal_view_degrees('rad') / 2) - camera.get_horizontal_view_degrees('rad') * Y_p
        v_VX = camera.get_vertical_view_degrees('rad') * X_p

        d3 = math.sin(camera.get_angle_to_floor('rad')-(camera.get_vertical_view_degrees('rad')/2)) * (camera.get_position()[2]/(math.cos(camera.get_angle_to_floor('rad')-(camera.get_vertical_view_degrees('rad')/2))))

        d5 = math.sin(v_HY) * (d3/math.cos(v_HY))

        d6 = (d5/math.sin(v_HY)) * math.tan(v_HY)
        d7 = sqrt((d1-math.cos(v_VX)*d6)**2 + (math.sin(v_VX)*d6)**2)

        v_px = math.atan(d5/(d3+d7))

        return v_px


    def _find_global_angle_between_camera_and_ellipses(self, camera, coordinate_ellispes):
        camera_position = camera.get_position()
        camera_x_y = (camera_position[0], camera_position[1])
        global_angles = []
        for ellipse in coordinate_ellispes:
            ellipse_x_y = (ellipse['coordinate']['coor'][0], ellipse['coordinate']['coor'][1])
            angle = math.atan((ellipse_x_y[1] - camera_x_y[1])/(ellipse_x_y[0] - camera_x_y[0]))
            global_angles.append(angle)
        return global_angles











#Nothing
