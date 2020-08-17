from Models.CameraModels import Camera
from Models.EllipseModels import Ellipse
from EllipseDetection import *
from Calibration import

from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
import cv2




class RobotTracking:
    def __init__(self, cam_info_list, circle_info_object, robot_info_object, visual_feedback):
        self.circle_info = circle_info_object       # circle_info.get_by_id(id); circle_info
        self.robot_info = robot_info_object         # robot_info.get_by_id(id); robot_info
        self.ellipse_detector = EllipseDetection(100)
        self.ellipse_filtering = EllipseFiltering(RobotEllipseRules())
        self.visual_feedback = visual_feedback
        self.cameras = self._init_cameras(cam_info_list)
        self.cam_calibration = CameraCalibration()

    def _init_cameras(self, cam_info_list):
        cameras = self._setup_cameras(cam_info_list)
        for cam in cameras:
            calibration_ellipses = []
            while len(calibration_ellipses) < 3:
                calibration_ellipses = self._get_calibration_ellipses(cam, frame_iterations=7)
            self.cam_calibration.calibrate(cam, calibration_ellipses, self.circle_info)
        return cameras

    def _setup_cameras(self, cam_info_list):
        camera_list = []
        for cam_count, cam_info in enumerate(cam_info_list):
            cam_name = 'cam_' + str(cam_count)
            cam = Camera(cam_info, cam_name)
            camera_list.append(cam)
        return camera_list

    def _get_calibration_ellipses(self, cam, frame_iterations):
        all_ellipses = self._get_robot_ellipses_over_N_iterations(cam, frame_iterations, 'calibration')
        number_of_cluster = self._estimate_number_of_clusters(len(all_ellipses), frame_iterations)
        cluster_centers = self._find_cluster_centers(all_ellipses, number_of_cluster)
        cali_robot_ellipses = self._represent_cluster_centers_as_ellipses(all_ellipses, cluster_centers)
        return cali_robot_ellipses

    def _estimate_number_of_clusters(self, number_of_points, number_of_iterations):
        return round(number_of_points / number_of_iterations)

    def _get_robot_ellipses_over_N_iterations(self, cam, nr_of_iterations, group = 'all'):
        all_ellipses = []
        for iteration in range(0, nr_of_iterations):
            frame = cam.get_frame()
            robot_ellipses = self._get_special_ellipses(cam, frame, group)
            all_ellipses.extend(robot_ellipses)
        return all_ellipses

    def _find_cluster_centers(self, ellipses, nr_of_clusters):                  #Mean shift clustering over nr_of_clusters
        ellipse_centers = [ellipse.get_center() for ellipse in ellipses]
        cluster_centers = self._find_N_cluster(ellipse_centers, nr_of_clusters)
        return cluster_centers

    def _auto_find_cluster_centers(self, ellipses):
        ellipse_centers = [ellipse.get_center() for ellipse in ellipses]
        current_nr_of_ellipses_in_range = 0
        previous_nr_of_ellipses_in_range = -1
        nr_of_clusters = 1
        previous_cluster_centers = []
        current_cluster_centers = []
        while current_nr_of_ellipses_in_range > previous_nr_of_ellipses_in_range:
            previous_nr_of_ellipses_in_range = current_nr_of_ellipses_in_range
            current_nr_of_ellipses_in_range  = 0
            previous_cluster_centers = current_cluster_centers
            current_cluster_centers = self._find_N_cluster(ellipse_centers, nr_of_clusters)
            print(current_cluster_centers)
            for center in current_cluster_centers:
                close_by_ellipse_centers = self._get_close_by_ellipses_from_center(ellipses, center)
                current_nr_of_ellipses_in_range += len(close_by_ellipse_centers)
            nr_of_clusters += 1
        return previous_cluster_centers


    def _find_N_cluster(self, points, nr_of_clusters):
        model = KMeans(n_clusters = nr_of_clusters)
        model.fit(points)
        centers = model.cluster_centers_
        return centers

    def _get_close_by_ellipses_from_center(self, ellipses, center):
        closest_ellipse = self._get_closest_ellipse_from_center(ellipses, center)
        ellipses_in_range = self._get_ellipses_in_range_of_ellipse(ellipses, closest_ellipse)
        return ellipses_in_range

    def _get_closest_ellipse_from_center(self, ellipses, center):
        closest_ellipse = ellipses[0]
        closest_distance = EllipseHelpFunction.length_between_centers(ellipses[0].get_center(), center)
        for ellipse in ellipses:
            distance = EllipseHelpFunction.length_between_centers(ellipse.get_center(), center)
            if distance < closest_distance:
                closest_ellipse = ellipse
                closest_distance = distance
        return closest_ellipse

    def _get_ellipses_in_range_of_ellipse(self, ellipses, center_ellipse):
        ellipses_in_range = []
        super_ellipse = center_ellipse.get_super_ellipse()
        for ellipse in ellipses:
            if center_ellipse != ellipse:
                if EllipseHelpFunction.check_if_points_is_inside_ellipse(super_ellipse, [ellipse.get_center()]) == True:
                    ellipses_in_range.append(ellipse)
        return ellipses_in_range

    def _represent_cluster_centers_as_ellipses(self, ellipses, cluster_centers):
        estimated_center_ellipses = []
        for center in cluster_centers:
            close_by_ellipse_centers = self._get_close_by_ellipses_from_center(ellipses, center)
            average_robot_ellipse = self._create_average_robot_ellipse(close_by_ellipse_centers)
            average_robot_ellipse.print()
            estimated_center_ellipses.append(average_robot_ellipse)
        return estimated_center_ellipses

    def _create_average_robot_ellipse(self, ellipses):
        nr_of_ellipses = len(ellipses)
        center_list = [ellipse.get_center() for ellipse in ellipses]
        average_center = [sum(center) / nr_of_ellipses for center in zip(*center_list)]
        average_width = sum([ellipse.get_width() for ellipse in ellipses]) / nr_of_ellipses
        average_height = sum([ellipse.get_height() for ellipse in ellipses]) / nr_of_ellipses
        average_rotation = sum([ellipse.get_rotation() for ellipse in ellipses]) / nr_of_ellipses
        average_angle = sum([ellipse.get_angle() for ellipse in ellipses]) / nr_of_ellipses
        average_distance = sum([ellipse.get_distance() for ellipse in ellipses]) / nr_of_ellipses

        average_super_ellipse = Ellipse([], average_center, average_width, average_height, average_rotation)
        average_robot_ellipse = RobotEllipse(super_ellipse = average_super_ellipse, sub_ellipses = ellipses[0].get_sub_ellipses())
        average_robot_ellipse.set_angle(average_angle)
        average_robot_ellipse.set_distance(average_distance)
        return average_robot_ellipse

    def find_robots(self):
        for cam in self.cameras:
            frame = cam.get_frame()
            robot_ellipses = self._get_special_ellipses(cam, frame, 'calibration')               #!
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

    def _get_special_ellipses(self, cam, frame, ellipse_group):
        color_corrected_frame = self._correct_colors_in_frame(frame)
        ellipses = self.ellipse_detector.detect(frame)
        special_ellipses = self.ellipse_filtering.filter(ellipses)
        robot_ellipses = self._convert_ellipses_to_robot_ellipses(special_ellipses)
        self._fill_in_robot_ellipses_info(robot_ellipses, cam)
        ellipse_group = self._get_ellipses_group(robot_ellipses, ellipse_group)
        return ellipse_group

    def _correct_colors_in_frame(self, frame):
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_frame = clahe.apply(gray_img)
        return clahe_frame

    def _convert_ellipses_to_robot_ellipses(self, ellipses):
        robot_ellipse_list = []
        for primary_ellipse in ellipses:
            robot_ellipse = self._create_robot_ellipse(primary_ellipse, ellipses)
            if robot_ellipse.valid() == True and self.circle_info.valid_id(robot_ellipse.get_id()) == True:
                robot_ellipse_list.append(robot_ellipse)
        return robot_ellipse_list

    def _create_robot_ellipse(self, primary_ellipse, ellipses):
        robot_ellipse = RobotEllipse(super_ellipse=primary_ellipse)
        for secondary_ellipse in ellipses:
            if primary_ellipse != secondary_ellipse:
                if self._if_super_ellipse(primary_ellipse, secondary_ellipse) == True:
                    robot_ellipse.add_sub_ellipse(secondary_ellipse)
        return robot_ellipse

    def _if_super_ellipse(self, primary_ellipse, secondary_ellipse):
        return EllipseHelpFunction.is_ellipse_inside_ellipse(secondary_ellipse, primary_ellipse)

    def _get_ellipses_group(self, robot_ellipses, group_name):
        robot_ellipse_group = []
        for robot_ellipse in robot_ellipses:
            if self.circle_info.valid_id(robot_ellipse.get_id()):
                if self.circle_info.get_type_by_id(robot_ellipse.get_id()) == group_name:
                    robot_ellipse_group.append(robot_ellipse)
        return robot_ellipse_group

    def _fill_in_robot_ellipses_info(self, robot_ellipses, cam):
        for robot_ellipse in robot_ellipses:
            dist_from_cam = self._calc_robot_ellipse_dist_from_cam(robot_ellipse, cam)
            angle_to_cam = self._calc_robot_ellipse_angle_to_cam(robot_ellipse)
            robot_ellipse.set_distance(dist_from_cam)
            robot_ellipse.set_angle(angle_to_cam)

    def _calc_robot_ellipse_dist_from_cam(self, robot_ellipse, cam):
        pixel_length_mm = self._calc_pixel_length_mm(robot_ellipse, cam)
        direct_image_length = self._dist_to_robot_ellipse(robot_ellipse, cam, pixel_length_mm)
        dist_from_center_mm = self._dist_from_center_mm(robot_ellipse, cam, pixel_length_mm)
        actual_length = math.sqrt(direct_image_length**2 + dist_from_center_mm**2)
        return actual_length

    def _calc_pixel_length_mm(self, robot_ellipse, cam):
        circle_size = self.circle_info.get_size_by_id(robot_ellipse.get_id())
        diameter = robot_ellipse.get_max_size() * 2
        pixel_length =  circle_size / diameter                                  #millimeters
        return pixel_length

    def _dist_to_robot_ellipse(self, robot_ellipse, cam, pixel_length_mm):
        image_height_mm = cam.get_size_from_known_degrees() * pixel_length_mm
        view_degrees_RAD = cam.get_cam_info().get_known_view_degrees('rad')
        unit_height = math.sin(view_degrees_RAD)
        unit_width = math.cos(view_degrees_RAD)
        height_ratio = (image_height_mm / 2) / unit_height
        triangle_width = height_ratio * unit_width
        return triangle_width

    def _dist_from_center_mm(self, robot_ellipse, cam, pixel_length_mm):
        width_diff = (cam.get_width()/2) - robot_ellipse.get_center('x')
        height_diff = (cam.get_height()/2) - robot_ellipse.get_center('y')
        width_diff_mm = width_diff * pixel_length_mm
        height_diff_mm = height_diff * pixel_length_mm
        direct_dist_from_center_mm = math.sqrt(width_diff_mm**2 + height_diff_mm**2)
        return direct_dist_from_center_mm

    def _calc_robot_ellipse_angle_to_cam(self, robot_ellipse):
        return math.acos(robot_ellipse.get_ratio()) * (180 / math.pi)









#Nothing
