from Models.CameraModels import Camera, CameraInfo
from Models.EllipseModels import Ellipse
from EllipseDetection import *
from Calibration import CameraCalibration
from SpecialEllipses import SpecialEllipses
from Tracking import RobotTracking as RT
from MarkerDetection import MarkerDetection
from Models.SquareModels import RobotSquare
from Robot import RobotTracking
from Resources import RobotResources, CircleResources, CameraInfoResouces
from Simulator import CamSimulatorImage

import matplotlib.pyplot as plt


marker_detection = MarkerDetection()

lenovo_cam_prob = CameraInfoResouces().get_camInfo_properties_by_name('Lenevo')
lenovo_cam_info = CameraInfo(address = 0, internal_properties = lenovo_cam_prob)

virtuel_cam = CamSimulatorImage(lenovo_cam_info, "Test_Image.JPG", "Cam_Test_Image")

frame = virtuel_cam.get_frame()

camera_matrix = virtuel_cam.get_cam_matrix()
distortion_coefficients = virtuel_cam.get_distortion_coeff()

img_undist = cv2.undistort(frame,camera_matrix,distortion_coefficients,None)
plt.subplot(211)
plt.imshow(frame)
plt.title("Raw image")
plt.axis("off")
plt.subplot(212)
plt.imshow(img_undist)
plt.title("Corrected image")
plt.axis("off")
plt.show()
