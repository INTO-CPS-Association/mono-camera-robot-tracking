from Visualizers import RobotVisualization

import math
import cv2
import numpy as np


class CameraInfo:
    def __init__(self, address, internal_properties = None):
        self.address = address
        self.internal_properties = internal_properties
        self.view_degrees_horizontal = None
        self.view_degrees_vertical = None
        self.dpi = None
        self.focal_length = None
        self.focus = None
        self.radial_distortion = None
        self._setup_camera_parameters(internal_properties)

    def _setup_camera_parameters(self, internal_properties):
        self.view_degrees_horizontal = self._get_dict_value(internal_properties, 'view_degrees_horizontal')
        self.view_degrees_vertical = self._get_dict_value(internal_properties, 'view_degrees_vertical')
        self.dpi = self._get_dict_value(internal_properties, 'dpi')
        self.focal_length = self._get_dict_value(internal_properties, 'focal_length')
        self.focus = self._get_dict_value(internal_properties, 'focus')
        self.radial_distortion = self._get_dict_value(internal_properties, 'radial_distortion')

    def _get_dict_value(self, dictonary, key):
        return dictonary[key] if key in dictonary else None

    def get_address(self):
        return self.address

    def get_view_degrees(self, type = 'deg'):
        if type.lower() == 'deg': return self.view_degrees
        elif type.lower() == 'rad': return math.radians(self.view_degrees)
        else: return self.view_degrees

    def get_dpi(self):
        return self.dpi

    def get_known_view_degrees(self, type = ''):
        if self.view_degrees_vertical != None:
            return self.get_vertical_view_degrees(type)
        else:
            return self.get_horizontal_view_degrees(type)

    def get_vertical_view_degrees(self, type = ''):
        if type == 'deg' or type == 'DEG': return self.view_degrees_vertical
        elif type == 'rad' or type == 'RAD': return math.radians(self.view_degrees_vertical)
        else: return self.view_degrees_vertical

    def set_vertical_view_degree(self, degree, type = ''):
        if type == 'rad' or type == 'RAD': self.view_degrees_vertical  = math.degrees(degree)
        else: self.view_degrees_vertical = degree

    def get_horizontal_view_degrees(self, type = ''):
        if type == 'deg' or type == 'DEG': return self.view_degrees_horizontal
        elif type == 'rad' or type == 'RAD': return math.radians(self.view_degrees_horizontal)
        else: return self.view_degrees_horizontal

    def set_horizontal_view_degree(self, degree, type = ''):
        if type == 'rad' or type == 'RAD': self.view_degrees_horizontal  = math.degrees(degree)
        else: self.view_degrees_horizontal = degree

    def get_focus(self):
        return self.focus

    def set_focus(self, focus):
        self.focus = focus









class CameraBase:
    def __init__(self, cam_info, cam_name = 'Cam'):
        self.name = cam_name
        self.cam_info = cam_info
        self.address = None
        self.init_status = False
        self.position = None    #(x, y, z)
        self.angle = None
        self.rotation = None
        self.visualizer = RobotVisualization(self.name)
        self._init(cam_info, cam_name)
        self.width = None
        self.height = None

    def _init(self, cam_info, cam_name):
        self.address = self._get_address(cam_info)

    def _get_address(self, cam_info):
        return cam_info.get_address()

    def get_frame(self):
        raise Exception("get_frame() is a pure function. Overload it to remove exception")

    def get_init_status(self):
        return self.init_status

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def get_angle_to_floor(self, type = ''):
        if type == 'rad' or type == 'RAD': return math.radians(self.angle)
        else: return self.angle

    def set_angle_to_floor(self, angle, type = ''):
        if type == 'rad' or type == 'RAD': self.angle = math.degrees(angle)
        else: self.angle = angle

    def set_rotation_from_center(self, rotation, type = ''):
        if type == 'rad' or type == 'RAD': self.rotation = math.degrees(rotation)
        else: self.rotation = rotation

    def get_rotation_from_center(self):
        return self.rotation

    def get_frame_size(self, type = ''):
        raise Exception("get_frame_sizse() is a pure function. Overload it to remove exception")

    def get_name(self):
        return self.name

    def update_frame(self, frame, data_object_list):
        self.visualizer.update_frame(frame.copy(), data_object_list)

    def get_width(self):
        return self.get_frame_size()[0]

    def get_height(self):
        return self.get_frame_size()[1]

    def get_cam_info(self):
        return self.cam_info

    def get_size_from_known_degrees(self, type = ''):
        if self.get_cam_info().get_vertical_view_degrees != None:
            return self.get_height()
        else:
            return self.get_width()

    def set_focus(self, focus):
        self.cam_info.set_focus(focus)

    def get_focus(self):
        return self.cam_info.get_focus()

    def get_horizontal_view_degrees(self, type = ''):
        return self.cam_info.get_horizontal_view_degrees(type)

    def set_horizontal_view_degree(self, degree, type = ''):
        return self.cam_info.set_horizontal_view_degree(degree, type)

    def get_vertical_view_degrees(self, type = ''):
        return self.cam_info.get_vertical_view_degrees(type)

    def set_vertical_view_degree(self, degree, type = ''):
        return self.cam_info.set_vertical_view_degree(degree, type)

    def get_cam_matrix(self):
        image_size = self.get_frame_size()
        image_center = (image_size[0]/2, image_size[1]/2)
        camera_matrix = [[image_size[0], 0,             image_center[0]], \
                         [0,             image_size[1], image_center[1]], \
                         [0,             0,             1]]
        np_camera_matrix = np.array(camera_matrix)
        return np_camera_matrix

    def get_distortion_coeff(self):
        distortion_coefficients = np.zeros((5, 1))
        return distortion_coefficients







class Camera(CameraBase):
    def __init__(self, cam_info, cam_name = 'Cam'):
        super().__init__(cam_info, cam_name)
        self.capture = None
        self._init_cam(cam_info, cam_name)

    def __del__(self):
        if self.capture != None:
            self.capture.release()
            cv2.destroyWindow(self.name)

    def _init_cam(self, cam_info, cam_name):
        self.capture = self._start_cam(self.address, cam_name)
        self.init_status = self._get_init_status(self.capture)
        self._set_cam_focus(cam_info.get_focus())

    def _set_cam_focus(self, focus):
        if focus != None:
            self.capture.set(28, focus)

    def _start_cam(self, cam_address, cam_name):
        capture = cv2.VideoCapture(cam_address)
        return capture

    def _get_init_status(self, capture):
        return capture.isOpened()

    def get_frame(self):
        rval, frame = self.capture.read()
        radial_frame = self._correct_radial_distortion(frame)
        down_scaled_frame = cv2.resize(radial_frame, (1280, 960), interpolation = cv2.INTER_AREA)
        return down_scaled_frame

    def _correct_radial_distortion(self, frame):                                #!
        return frame

    def get_frame_size(self, type = ''):
        if type == 'x' or type == 'X':
            return self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        elif type == 'y' or type == 'Y':
            return self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        else:
            return (self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))








#Nothing
