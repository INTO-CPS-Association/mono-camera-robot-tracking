from Robot import RobotTracking
from Communication import Subscribers
from Models.CameraModels import CameraInfo
from RobotResources import RobotResources, CircleResources
import time

camera_properties = {   'view_degrees_horizontal': 80,
                        'view_degrees_vertical': None,
                        'dpi': None,
                        'focal_length': None,
                        'focus': None }

cam_info = CameraInfo(address = 1, internal_properties = camera_properties)
circle_info = CircleResources()
robot_info = RobotResources()

tracking = RobotTracking([cam_info], circle_info, robot_info, visual_feedback = True)
robot_subs = Subscribers('robot')

while True:
    timestamp = time.time()
    robot_list = tracking.find_robots()
    if robot_list == -1: break

    for robot in robot_list:
        subs = robot_subs.robot_position(robot)
        robot_subs.send_to(subs, robot.position, timestamp)
