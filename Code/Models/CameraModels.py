from Visualizers import RobotVisualization

import math
import cv2


class CameraInfo:
    def __init__(self, address, internal_properties = None):
        self.address = address
        self.internal_properties = internal_properties
        self.view_degrees_horizontal = None
        self.view_degrees_vertical = None
        self.dpi = None
        self.focal_length = None
        self.focus = None
        self._setup_camera_parameters(internal_properties)

    def _setup_camera_parameters(self, internal_properties):
        self.view_degrees_horizontal = self._get_dict_value(internal_properties, 'view_degrees_horizontal')
        self.view_degrees_vertical = self._get_dict_value(internal_properties, 'view_degrees_vertical')
        self.dpi = self._get_dict_value(internal_properties, 'dpi')
        self.focal_length = self._get_dict_value(internal_properties, 'focal_length')
        self.focus = self._get_dict_value(internal_properties, 'focus')

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
        if type.lower() == 'deg': return self.view_degrees_vertical
        elif type.lower() == 'rad': return math.radians(self.view_degrees_vertical)
        else: return self.view_degrees_vertical

    def get_horizontal_view_degrees(self, type = ''):
        if type.lower() == 'deg': return self.view_degrees_horizontal
        elif type.lower() == 'rad': return math.radians(self.view_degrees_horizontal)
        else: return self.view_degrees_horizontal

    def get_focus(self):
        return self.focus



class Camera:
    def __init__(self, cam_info, cam_name = 'Cam'):
        self.name = cam_name
        self.cam_info = cam_info
        self.address = None
        self.capture = None
        self.init_status = False
        self.position = (0, 0, 0)    #x, y, z
        self.visualizer = RobotVisualization(self.name)
        self._init_cam(cam_info, cam_name)
        self.width = None
        self.height = None

    def __del__(self):
        if self.capture != None:
            self.capture.release()
            cv2.destroyWindow(self.name)

    def _init_cam(self, cam_info, cam_name):
        self.address = self._get_address(cam_info)
        self.capture = self._start_cam(self.address, cam_name)
        self.init_status = self._get_init_status(self.capture)
        self._set_cam_focus(cam_info.get_focus())

    def _set_cam_focus(self, focus):
        if focus != None:
            self.capture.set(28, focus)

    def _get_address(self, cam_info):
        return cam_info.get_address()

    def _start_cam(self, cam_address, cam_name):
        capture = cv2.VideoCapture(cam_address)
        return capture

    def _get_init_status(self, capture):
        return capture.isOpened()

    def get_frame(self):
        rval, frame = self.capture.read()
        radial_frame = self._correct_radial_distortion(frame)
        #down_scaled_frame = cv2.resize(radial_frame, (640, 480), interpolation = cv2.INTER_AREA)
        return radial_frame

    def _correct_radial_distortion(self, frame):                                #!
        return frame

    def get_init_status(self):
        return self.init_status

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def get_frame_size(self):
        return (self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_name(self):
        return self.name

    def update_frame(self, frame, data_object_list):
        self.visualizer.update_frame(frame, data_object_list)

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
