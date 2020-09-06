from Models.CameraModels import Camera
from Models.EllipseModels import Ellipse
from EllipseDetection import *
from Calibration import CameraCalibration
from SpecialEllipses import SpecialEllipses

import cv2
import operator
import random



class RobotTracking:
    def __init__(self, cam_info_list, circle_info_object, robot_info_object, visual_feedback):
        self.circle_info = circle_info_object       # circle_info.get_by_id(id); circle_info
        self.robot_info = robot_info_object         # robot_info.get_by_id(id); robot_info
        self.special_ellipses = SpecialEllipses(100)
        self.ellipse_filtering = EllipseFiltering(RobotEllipseRules())
        self.visual_feedback = visual_feedback
        self.cam_calibration = CameraCalibration()
        self.cameras = self._init_cameras(cam_info_list)

    def _init_cameras(self, cam_info_list):
        cameras = self._setup_cameras(cam_info_list)
        for cam in cameras:
            self._calibrate_camera_focus(cam)
            calibration_ellipses = []
            # while len(calibration_ellipses) < 3:
            #     calibration_ellipses = self._get_calibration_ellipses(cam, frame_iterations=7)
            # self.cam_calibration.calibrate(cam, calibration_ellipses, self.circle_info)
        return cameras

    def _calibrate_camera_focus(self, cam, combinations = 8):
        if cam.get_focus() != None:
            return

        frame = cam.get_frame()
        focus_range = [0, 255]
        step_size = int(focus_range[1] / 8)

        focus_strengths = []
        for focus_level in range(focus_range[0], focus_range[1], step_size):
            cam.set_focus(focus_level)
            ellipses = self.special_ellipses.get_raw_ellipses(cam, frame)
            strength = len(ellipses)
            focus_strengths.append((focus_level, strength))

        focus = max(focus_strengths, key=operator.itemgetter(1))[0]
        cam.set_focus(focus)



    def _setup_cameras(self, cam_info_list):
        camera_list = []
        for cam_count, cam_info in enumerate(cam_info_list):
            cam_name = 'cam_' + str(cam_count)
            cam = Camera(cam_info, cam_name)
            camera_list.append(cam)
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
            robot_ellipses = self._get_ellipses_from_group(cam, frame, 'robot')
            robot_positions = self._generate_robot_positions_test(robot_ellipses)
            self._append_positions_to_dict(all_robot_positions, robot_positions)
            status = self._visualize(cam, frame, robot_ellipses)
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
        model_list = [self.circle_info.get_model_by_id(robot_ellipse.get_id()) for robot_ellipse in robot_ellipses]
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
        robot_ellipses = self.special_ellipses.get_from_frame(cam, frame, self.circle_info)
        group_ellipses = self._get_ellipses_group(robot_ellipses, ellipse_group)
        self._fill_in_robot_ellipses_info(group_ellipses, cam)
        return group_ellipses

    def _get_ellipses_group(self, robot_ellipses, ellipse_group):
        robot_ellipse_group = []
        for robot_ellipse in robot_ellipses:
            if self.circle_info.valid_id(robot_ellipse.get_id()):
                if self.circle_info.get_type_by_id(robot_ellipse.get_id()) == ellipse_group:
                    robot_ellipse_group.append(robot_ellipse)
        return robot_ellipse_group

    def _fill_in_robot_ellipses_info(self, robot_ellipses, cam):
        for robot_ellipse in robot_ellipses:
            distance = self.special_ellipses.calc_distance(robot_ellipse, cam, self.circle_info)
            angle = self.special_ellipses.calc_angle(robot_ellipse)
            robot_ellipse.set_distance(distance)
            robot_ellipse.set_angle(angle)










#Nothing
