from Models.CameraModels import CameraBase
import cv2

class CamSimulatorImage(CameraBase):
    def __init__(self, cam_info, image_address, cam_name = 'Cam'):
        super().__init__(cam_info, cam_name)
        self.image_address = image_address
        self._frame = None
        self._size = None
        self._init_cam(image_address)

    def _init_cam(self, image_address):
        self._frame = cv2.imread(image_address)
        if self._frame is not None:
            self.init_status = True
            self._size = (self._frame.shape[1], self._frame.shape[0])

    def get_frame(self):
        return self._frame

    def get_frame_size(self, type = ''):
        if type == 'x' or type == 'X':
            return self._size[0]
        elif type == 'y' or type == 'Y':
            return self._size[1]
        else:
            return self._size






class CamSimulatorEllipse(CameraBase):
    def __init__(self):
        pass








#Nothing
