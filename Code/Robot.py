from Models.CameraModels import Camera
from Models.EllipseModels import Ellipse
from EllipseDetection import *
from Calibration import CameraCalibration
from SpecialEllipses import SpecialEllipses

import cv2
import operator




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
        for cam in self.cameras:
            frame = cam.get_frame()
            robot_ellipses = self._get_ellipses_from_group(cam, frame, 'calibration')
            status = self._visualize(cam, frame, robot_ellipses)
            if status == -1:
                return -1
        return []

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
