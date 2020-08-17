from Models.EllipseModels import *
import cv2



class RobotVisualization:
    def __init__(self, window_name):
        self.window_name = window_name

    def update_frame(self, frame, data_object_list):
        for data_object in data_object_list:
            if isinstance(data_object, Ellipse):
                frame = self._visualize_ellipse(frame, data_object)
            elif isinstance(data_object, RobotEllipse):
                frame = self._visualize_robot_ellipse(frame, data_object)
        cv2.imshow(self.window_name, frame)

    def _visualize_ellipse(self, frame, ellipse):
        center = (int(ellipse.center('y')), int(ellipse.center('x')))
        axes = (int(ellipse.width()), int(ellipse.height()))
        rotation = int(ellipse.rotation())
        if ellipse.rotation() < 0:
            rotation = -rotation
        color = (0, 0, 255)
        thickness = 1
        return cv2.ellipse(frame, center, axes, rotation, 0, 360, color, thickness)

    def _visualize_robot_ellipse(self, frame, robot_ellipse):
        frame = self._visualize_ellipse(frame, robot_ellipse.get_super_ellipse())
        for ellipse in robot_ellipse.get_sub_ellipses():
            frame = self._visualize_ellipse(frame, ellipse)
        frame = self._visualize_robot_ellipse_text_info(frame, robot_ellipse)
        return frame

    def _visualize_robot_ellipse_text_info(self, frame, robot_ellipse):
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.5
        color = (0, 0, 255)
        thickness = 2
        text_seperation_length = 20
        center = (int(robot_ellipse.get_center('y')), int(robot_ellipse.get_center('x')))
        frame = cv2.circle(frame, center, 4, (0, 255, 0), 2)
        start_x_pos = robot_ellipse.get_center('x')
        start_y_pos = robot_ellipse.get_center('y') + robot_ellipse.get_width() + 5
        
        org = (int(start_y_pos), int(start_x_pos)+text_seperation_length*0)
        frame = cv2.putText(frame, 'L: ' + str(int(robot_ellipse.get_distance())), org, font, fontScale*1.4, color, thickness, cv2.LINE_AA)
        org = (int(start_y_pos), int(start_x_pos)+text_seperation_length*1)
        frame = cv2.putText(frame, 'R: ' + str(int(robot_ellipse.get_rotation())), org, font, fontScale*1.4, color, thickness, cv2.LINE_AA)
        org = (int(start_y_pos), int(start_x_pos)+text_seperation_length*2)
        frame = cv2.putText(frame, 'A: ' + str(int(robot_ellipse.get_angle())), org, font, fontScale*1.4, color, thickness, cv2.LINE_AA)
        org = (int(start_y_pos), int(start_x_pos)+text_seperation_length*3)
        frame = cv2.putText(frame, 'ID: ' + str(robot_ellipse.get_id()), org, font, fontScale, color, thickness, cv2.LINE_AA)
        return frame

    def _visualize_robot_boundaries(self, frame, robot):
        pass
