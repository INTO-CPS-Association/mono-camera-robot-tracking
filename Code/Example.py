from Robot import RobotTracking
from Models.CameraModels import CameraInfo
from Resources import RobotResources, CircleResources, CameraInfoResouces
from Simulator import CamSimulatorImage
import time

lenovo_cam_prob = CameraInfoResouces().get_camInfo_properties_by_name('Lenevo')
lenovo_cam_info = CameraInfo(address = 0, internal_properties = lenovo_cam_prob)

virtuel_cam = CamSimulatorImage(lenovo_cam_info, "Test_Image.JPG", "Cam_Test_Image")

circle_info = CircleResources()
robot_info = RobotResources()

tracking_simulator = RobotTracking(marker_info_object=circle_info, robot_info_object=robot_info, cameras=[virtuel_cam], cam_info_list=[], visual_feedback=True)
#tracking = RobotTracking([lenovo_cam_info], circle_info, robot_info, visual_feedback = True, cameras = [virtuel_cam])

while True:
    timestamp = time.time()
    robot_list = tracking_simulator.find_robots()

    if robot_list == -1: break

    for robot in robot_list:
        print(robot)
