from Models.CameraModels import Camera
from Models.EllipseModels import Ellipse
from EllipseDetection import *
from Calibration import CameraCalibration
from SpecialEllipses import SpecialEllipses
from Tracking import RobotTracking as RT
from MarkerDetection import MarkerDetection
from Models.SquareModels import RobotSquare

import cv2
import operator
import random



class RobotTracking:
    def __init__(self, marker_info_object, robot_info_object, cam_info_list = [], cameras = [], visual_feedback = False):
        self.marker_info = marker_info_object
        self.robot_info = robot_info_object
        self.visual_feedback = visual_feedback
        self.marker_detection = MarkerDetection()
        self.cam_calibration = CameraCalibration()
        self.cameras = self._init_cameras(cam_info_list, cameras)
        self.robot_tracking = RT(self.marker_info, self.robot_info)

    def _init_cameras(self, cam_info_list, cameras):
        cameras = self._setup_cameras(cam_info_list, cameras)
        for cam in cameras:
            self._calibrate_camera_focus(cam)
            self._calculate_missing_view_degree(cam)
            calibration_markers = self._get_squares_from_group(cam, cam.get_frame(), 'calibration')
            for marker in calibration_markers: marker.print()

            #calibration_ellipses = self._generate_stub_ellipses()
            #self.cam_calibration.calibrate(cam, calibration_markers, self.marker_info)
        return cameras

    def _calculate_missing_view_degree(self, cam):
        frame_size = cam.get_frame_size()
        ratio = frame_size[0] / frame_size[1]
        if cam.get_horizontal_view_degrees() != None and cam.get_vertical_view_degrees() == None:
            angle_horizontal = cam.get_horizontal_view_degrees()
            angle_vertical = angle_horizontal * ratio
            cam.set_vertical_view_degree(angle_vertical)
        elif cam.get_horizontal_view_degrees() == None and cam.get_vertical_view_degrees() != None:
            angle_vertical = cam.get_vertical_view_degrees()
            angle_horizontal = angle_vertical / ratio
            cam.set_vertical_view_degree(angle_horizontal)

    def _calculate_view_degree(self, cam, height, distance):
        return math.atan((height/2) / distance)

    def _generate_stub_ellipses(self):
        sub_ellipse_stub = Ellipse([],(0, 0), 0, 0, 0)   #Data does not matter for a sub ellipse

        super_ellipse_1 = Ellipse([], (100, 100), 100, 50, 0)
        sub_ellipses_1 = [sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub]
        calibration_ellipse_1 = RobotEllipse(super_ellipse_1, sub_ellipses_1, 2455, 33.39)

        super_ellipse_2 = Ellipse([], (200, 200), 100, 50, 0)
        sub_ellipses_2 = [sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub]
        calibration_ellipse_2 = RobotEllipse(super_ellipse_2, sub_ellipses_2, 2848, 28.29)

        super_ellipse_3 = Ellipse([], (300, 100), 100, 50, 0)
        sub_ellipses_3 = [sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub, sub_ellipse_stub]
        calibration_ellipse_3 = RobotEllipse(super_ellipse_3, sub_ellipses_3, 2632, 30.86)

        calibration_ellipses = [calibration_ellipse_1, calibration_ellipse_2, calibration_ellipse_3]
        return calibration_ellipses

    def _calibrate_camera_focus(self, cam, combinations = 8):
        if cam.get_focus() != None:
            return
        if self.visual_feedback == True:
            print("Setting cam up: ")

        frame = cam.get_frame()
        focus_range = [0, 255]
        step_size = int(focus_range[1] / 8)

        focus_strengths = []
        for focus_level in range(focus_range[0], focus_range[1], step_size):
            if self.visual_feedback == True:
                print(str(int(focus_level/step_size)) + "/" + str(int(focus_range[1]/step_size)))
            cam.set_focus(focus_level)
            markers = self.marker_detection.get_markers(frame)
            strength = len(markers)
            focus_strengths.append((focus_level, strength))

        focus = max(focus_strengths, key=operator.itemgetter(1))[0]
        cam.set_focus(focus)



    def _setup_cameras(self, cam_info_list, cameras):
        camera_list = []
        for cam_count, cam_info in enumerate(cam_info_list):
            cam_name = 'cam_' + str(cam_count)
            cam = Camera(cam_info, cam_name)
            camera_list.append(cam)
        for camera in cameras:
            camera_list.append(camera)
        return camera_list

    def _get_calibration_ellipses(self, cam, frame_iterations):
        all_ellipses = self._get_robot_ellipses_over_N_iterations(cam, frame_iterations, 'calibration')
        cali_robot_ellipses = self.special_ellipses.find_standard_representations(all_ellipses, frame_iterations)
        return cali_robot_ellipses

    def _get_robot_ellipses_over_N_iterations(self, cam, nr_of_iterations, group = 'all'):
        all_ellipses = []
        for _ in range(nr_of_iterations):
            frame = cam.get_frame()
            robot_ellipses = self._get_ellipses_from_group(cam, frame, 'calibration')
            all_ellipses.extend(robot_ellipses)
        return all_ellipses




    def find_robots(self):
        all_robot_positions = {}
        for cam in self.cameras:
            frame = cam.get_frame()
            robot_squares = self._get_squares_from_group(cam, frame, 'calibration')
            #robot_positions = self.robot_tracking.get_positions(robot_ellipses)
            #self._append_positions_to_dict(all_robot_positions, robot_positions)
            status = self._visualize(cam, frame, robot_squares)
            if status == -1:
                return -1
        positions = self._concentrate_robot_positions(all_robot_positions)
        return positions

    def _concentrate_robot_positions(self, robot_position_map):
        final_positions = []
        for model_key in robot_position_map:
            position = robot_position_map[model_key][0]
            final_positions.append({'model': model_key, 'position': position})
        return final_positions

    def _append_positions_to_dict(self, position_dict, new_positions):
        for position in new_positions:
            model = position['name']
            coordinate = position['position']
            if model not in position_dict:
                position_dict[model] = []
            position_dict[model].append(coordinate)

    def _set_of_robot_models(self, robot_ellipses):
        model_list = [self.marker_info.get_model_by_id(robot_ellipse.get_id()) for robot_ellipse in robot_ellipses]
        model_set = set(model_list)
        return model_set

    def _generate_robot_positions_test(self, robot_ellipses):
        robot_models = self._set_of_robot_models(robot_ellipses)
        robots_position = []
        for count, robot_model in enumerate(robot_models):
            dist = robot_ellipses[count].get_distance()
            robot_position = { 'name': robot_model, 'position': { 'x': int(dist), 'y': int(dist/2), 'z': 0, 'r': dist/1000 } }
            robots_position.append(robot_position)
        return robots_position

    def _visualize(self, cam, frame, robot_ellipses):
        if self.visual_feedback == True:
            cam.update_frame(frame, robot_ellipses)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return -1
        return 1

    def _get_ellipses_from_group(self, cam, frame, ellipse_group):
        #robot_ellipses = self.special_ellipses.get_from_frame(cam, frame, self.marker_info)     #THIS IS THE ONLY ONE THAT SHOULD BE SGITED OUT WITH THE NEW METHOD
        markers = self.marker_detection.get_markers(frame)
        robot_ellipses = self.marker_detection.get_robot_ellipses(cam, frame, markers)
        group_ellipses = self._get_ellipses_group(robot_ellipses, ellipse_group)
        self._fill_in_robot_ellipses_info(group_ellipses, cam)
        return group_ellipses

    def _get_squares_from_group(self, cam, frame, group_name):
        markers = self.marker_detection.get_markers(frame)
        robot_squares = self.marker_detection.get_robot_squares(markers)
        group_squares = self._get_square_groups(robot_squares, group_name)
        self._fill_in_robot_squares_info(group_squares, cam)
        return group_squares

    def _get_square_groups(self, robot_squares, group_name):
        robot_square_group = []
        for robot_square in robot_squares:
            if self.marker_info.valid_id(robot_square.get_id()):
                if self.marker_info.get_type_by_id(robot_square.get_id()) == group_name:
                    robot_square_group.append(robot_square)
        return robot_square_group

    def _get_ellipses_group(self, robot_ellipses, ellipse_group):
        robot_ellipse_group = []
        for robot_ellipse in robot_ellipses:
            if self.marker_info.valid_id(robot_ellipse.get_id()):
                if self.marker_info.get_type_by_id(robot_ellipse.get_id()) == ellipse_group:
                    robot_ellipse_group.append(robot_ellipse)
        return robot_ellipse_group

    def _fill_in_robot_ellipses_info(self, robot_ellipses, cam):
        for robot_ellipse in robot_ellipses:
            distance = self.special_ellipses.calc_distance(robot_ellipse, cam, self.marker_info)
            angle = self.special_ellipses.calc_angle(robot_ellipse)
            robot_ellipse.set_distance(distance)
            robot_ellipse.set_angle(angle)

    def _fill_in_robot_squares_info(self, robot_squares, cam):
        for robot_square in robot_squares:
            corners = robot_square.get_corners()
            square_side_length = self.marker_info.get_size_by_id(robot_square.get_id())
            rotation_vector, translation_vector = self.marker_detection.calc_rotation_translation_matrix(corners, square_side_length, cam)

            rot_vec = rotation_vector
            rot_mat = cv2.Rodrigues(rot_vec[0][0])
            print("(" + str(robot_square.get_id()) + ") Rotation Matrix: " + str(rot_vec))
            print("(" + str(robot_square.get_id()) + ") Translation Matrix: " + str(translation_vector))
            print(rot_mat)
            print("----------")

            distance =  self._calculate_distance_to_square(rotation_vector, translation_vector)
            angle =  self._calculate_square_angle(rotation_vector)

            robot_square.set_distance(distance)
            robot_square.set_angle(angle, 'deg')

    def _calculate_distance_to_square(self, rotation_matrix, translation_matrix):
        tmat = translation_matrix[0][0] * 100
        realDistanceInTvec = self.euclideanDistanceOfTvec(tmat)
        return realDistanceInTvec


    def _calculate_square_angle(self, rotation_matrix):
        return (rotation_matrix[0][0][2] / math.pi * 180)

    def euclideanDistanceOfTvecs(self, tvec1, tvec2):
        return math.sqrt(math.pow(tvec1[0]-tvec2[0], 2) + math.pow(tvec1[1]-tvec2[1], 2) + math.pow(tvec1[2]-tvec2[2], 2))

    def euclideanDistanceOfTvec(self, tvec):
        return self.euclideanDistanceOfTvecs(tvec, [0, 0, 0])







#Nothing
