from Robot import RobotTracking
from Models.CameraModels import CameraInfo
from Resources import RobotResources, CircleResources, CameraInfoRecouces
import time

from ExtraHelpTools import CameraInformationHelpTool

camInfos = CameraInfoRecouces()
logitec_prob = { 'view_degrees_vertical': 26.14 }

cam_info = CameraInfo(address = 0, internal_properties = logitec_prob)
circle_info = CircleResources()
robot_info = RobotResources()

tracking = RobotTracking([cam_info], circle_info, robot_info, visual_feedback = True)

while True:
    timestamp = time.time()
    robot_list = tracking.find_robots()
    
    if robot_list == -1: break

    for robot in robot_list:
        print(robot)
