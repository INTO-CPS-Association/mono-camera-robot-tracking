from EllipseDetection import *

from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
import cv2
import operator

class SpecialEllipses:
    def __init__(self, error_threshold):
        self.ellipse_detector = EllipseDetection(error_threshold)
        self.ellipse_filtering = EllipseFiltering(RobotEllipseRules())

    def get_raw_ellipses(self, cam, frame):
        color_corrected_frame = self._correct_colors_in_frame(frame)
        ellipses = self.ellipse_detector.detect(color_corrected_frame)
        return ellipses

    def get_from_frame(self, cam, frame, circle_info):
        return self._get_special_ellipses(cam, frame, circle_info)

    def calc_distance(self, robot_ellipse, cam, circle_info):
        pixel_length_mm = self._calc_pixel_length_mm(robot_ellipse, cam, circle_info)
        direct_image_length = self._dist_to_robot_ellipse(robot_ellipse, cam, pixel_length_mm)
        dist_from_center_mm = self._dist_from_center_mm(robot_ellipse, cam, pixel_length_mm)
        actual_length = math.sqrt(direct_image_length**2 + dist_from_center_mm**2)
        return actual_length

    def calc_angle(self, robot_ellipse):
        return math.acos(robot_ellipse.get_ratio()) * (180 / math.pi)

    def find_standard_representations(self, robot_ellipses, frame_iterations = 1):
        number_of_cluster = self._estimate_number_of_clusters(len(robot_ellipses), frame_iterations)
        cluster_centers = self._find_cluster_centers(robot_ellipses, number_of_cluster)
        cali_robot_ellipses = self._represent_cluster_centers_as_ellipses(robot_ellipses, cluster_centers)
        return cali_robot_ellipses

    def _get_special_ellipses(self, cam, frame, circle_info):
        color_corrected_frame = self._correct_colors_in_frame(frame)
        ellipses = self.ellipse_detector.detect(color_corrected_frame)
        special_ellipses = self.ellipse_filtering.filter(ellipses)
        robot_ellipses = self._convert_ellipses_to_robot_ellipses(special_ellipses, circle_info)
        robot_ellipses = self._filter_out_double_ellipses(robot_ellipses)
        return robot_ellipses

    def _filter_out_double_ellipses(self, robot_ellipses):
        filtered_robot_ellipses = []
        for robot_ellipse in robot_ellipses:
            if self._robot_ellipses_inside_of_ellipse(robot_ellipses, robot_ellipse) == False:
                filtered_robot_ellipses.append(robot_ellipse)
        return filtered_robot_ellipses

    def _robot_ellipses_inside_of_ellipse(self, robot_ellipses, robot_ellipse):
        for robot_ellipse_check in robot_ellipses:
            if robot_ellipse_check != robot_ellipse:
                inner_ellipse = robot_ellipse_check.get_super_ellipse()
                outer_ellipse = robot_ellipse.get_super_ellipse()
                if EllipseHelpFunction.is_ellipse_inside_ellipse(inner_ellipse, outer_ellipse):
                    return True
        return False

    def _correct_colors_in_frame(self, frame):
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_frame = clahe.apply(gray_img)
        return clahe_frame

    def _convert_ellipses_to_robot_ellipses(self, ellipses, circle_info):
        robot_ellipse_list = []
        for primary_ellipse in ellipses:
            robot_ellipse = self._create_robot_ellipse(primary_ellipse, ellipses)
            if robot_ellipse.valid() == True and circle_info.valid_id(robot_ellipse.get_id()) == True:
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

    def _calc_pixel_length_mm(self, robot_ellipse, cam, circle_info):
        circle_size_mm = circle_info.get_size_by_id(robot_ellipse.get_id())
        diameter_px = robot_ellipse.get_max_size() * 2
        pixel_length_mm =  circle_size_mm / diameter_px                
        return pixel_length_mm

    def _dist_to_robot_ellipse(self, robot_ellipse, cam, pixel_length_mm):
        image_size_mm = cam.get_size_from_known_degrees() * pixel_length_mm
        view_angle_RAD = cam.get_cam_info().get_known_view_degrees('rad')

        unit_size = math.sin(view_angle_RAD/2)
        unit_dist = math.cos(view_angle_RAD/2)

        size_factor = image_size_mm / unit_size
        distance = unit_dist * size_factor

        return distance

    def _dist_from_center_mm(self, robot_ellipse, cam, pixel_length_mm):
        width_diff = (cam.get_width()/2) - robot_ellipse.get_center('x')
        height_diff = (cam.get_height()/2) - robot_ellipse.get_center('y')
        width_diff_mm = width_diff * pixel_length_mm
        height_diff_mm = height_diff * pixel_length_mm
        direct_dist_from_center_mm = math.sqrt(width_diff_mm**2 + height_diff_mm**2)
        return direct_dist_from_center_mm

    def _estimate_number_of_clusters(self, number_of_points, number_of_iterations):
        return round(number_of_points / number_of_iterations)

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
        average_sub_ellipses = self._create_average_sub_ellipses(ellipses)
        average_robot_ellipse = RobotEllipse(super_ellipse = average_super_ellipse, sub_ellipses = average_sub_ellipses)
        average_robot_ellipse.set_angle(average_angle)
        average_robot_ellipse.set_distance(average_distance)
        return average_robot_ellipse

    def _create_average_sub_ellipses(self, ellipses):
        id_map = {}
        for ellipse in ellipses:
            if ellipse.get_id() not in id_map:
                id_map[ellipse.get_id()] = 0
            id_map[ellipse.get_id()] += 1
        dominant_id = max(id_map.items(), key=operator.itemgetter(1))[0]
        for ellipse in ellipses:
            if ellipse.get_id() == dominant_id:
                return ellipse.get_sub_ellipses()
        return ellipses[0].get_sub_ellipses()
