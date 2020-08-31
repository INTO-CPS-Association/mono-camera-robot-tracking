from Models.EllipseModels import *

from skimage import measure
import numpy as np
import math
import cv2



class EllipseDetection:
    def __init__(self, ellipse_threshold = 50):
        self._ellipse_error_threshold = ellipse_threshold

    def detect(self, image):
        edge_image = self._edge_detection_and_linking(image)
        edges = self._find_individual_edges(edge_image)
        ellipses = self._detect_ellipses(edges, image)
        return ellipses

    def _edge_detection_and_linking(self, image):                               #(y)
        return cv2.Canny(image, 100, 200)

    def _find_individual_edges(self, edge_image):                               #(y)
        labels = measure.label(edge_image)
        edges = self._find_edges_from_labels(labels)
        pure_edges = self._convert_to_pure_edges(edges)
        filtered_pure_edges = self._edge_filtering(pure_edges)
        return filtered_pure_edges

    def _find_edges_from_labels(self, labels):                                  #!
        edges = {}
        for label_nr, label in enumerate(labels):
            for element_nr, element in enumerate(label):
                if element != 0:
                    if element not in edges: edges[element] = []
                    edges[element].append([label_nr, element_nr])       #[[edge_group, edge_pixel], ...]
        return edges

    def _convert_to_pure_edges(self, edges):
        return [edges[key] for key in edges]

    def _edge_filtering(self, pure_edges):
        filtered_edges = []
        for edge in pure_edges:
            if len(edge) > 10:
             diff_list_x = [abs(edge[count][0] - edge[count+1][0]) for count in range(0, len(edge)-1)]
             diff_list_y = [abs(edge[count][1] - edge[count+1][1]) for count in range(0, len(edge)-1)]
             diff_norm_x = sum(diff_list_x) / len(edge)
             diff_norm_y = sum(diff_list_y) / len(edge)
             if diff_norm_x >= 0.2 and diff_norm_y >= 0.2:
                 filtered_edges.append(edge)
        return filtered_edges

    def _detect_ellipses(self, edges, image):
        all_ellipses = self._find_all_ellipses(edges)
        ellipses = self._filter_ellipses(all_ellipses, image)
        return ellipses

    def _find_all_ellipses(self, edges):
        ellipse_list = []
        for edge in edges:
            ellipse = self._ellipse_detection(edge)
            ellipse_list.append(ellipse)
        return ellipse_list

    def _ellipse_detection(self, edge):
        original_ellipse = self._calculate_ellipse_from_edge(edge)
        centered_edge = [[coor[0] - original_ellipse.center('x'), coor[1] - original_ellipse.center('y')] for coor in edge]
        centered_ellipse = self._calculate_ellipse_from_edge(centered_edge)
        original_ellipse.width = centered_ellipse.width
        original_ellipse.height = centered_ellipse.height
        return original_ellipse

    def _calculate_ellipse_from_edge(self, edge):                                         #!
        a_matrix = self._calculate_a_matrix(edge)
        b_matrix = self._calculate_b_matrix(edge)
        result_matrix = self._calculate_least_square_result(a_matrix, b_matrix, edge)
        if isinstance(result_matrix, (np.ndarray, np.generic) ) == False:
            return Ellipse(edge, (0, 0), 1, 1000, 0)
        center = self._calculate_center_coor_approx(result_matrix)
        rotation = self._calculate_ellipse_rotation(result_matrix)
        width = self._calculate_ellipse_width(result_matrix, center)
        height = self._calculate_ellipse_height(result_matrix, center)
        return Ellipse(edge, center, width, height, rotation)

    def _calculate_ellipse_rotation(self, result_matrix):
        if (result_matrix[0][0]-1) != 0:
            hypotenuse = (2*result_matrix[1][0])/(result_matrix[0][0]-1)
        else:
            hypotenuse = 9999
        return math.degrees(0.5*math.atan(hypotenuse))

    def _calculate_ellipse_width(self, result_matrix, center):
        width_first = 2*(result_matrix[4][0]+(center[1]*center[1])+(center[0]*center[0])*result_matrix[0][0]+2*result_matrix[1][0])
        width_second =  (1+result_matrix[0][0])-math.sqrt(((1-result_matrix[0][0])*(1-result_matrix[0][0]))+(4*(result_matrix[1][0]*result_matrix[1][0])))
        if width_second != 0:
            width_full = width_first / width_second
        else:
            width_full = 9999
        width = math.sqrt(abs(width_full))
        return width

    def _calculate_ellipse_height(self, result_matrix, center):
        height_first = 2*(result_matrix[4][0]+(center[1]*center[1])+(center[0]*center[0])*result_matrix[0][0]+2*result_matrix[1][0])
        height_second =  (1+result_matrix[0][0])+math.sqrt(((1-result_matrix[0][0])*(1-result_matrix[0][0]))+(4*(result_matrix[1][0]*result_matrix[1][0])))
        height_full = height_first / height_second
        height = math.sqrt(abs(height_full))
        return height

    def _calculate_a_matrix(self, coordinate_list):
        a_matrix = np.zeros(shape=(len(coordinate_list), 5))
        for count, coor in enumerate(coordinate_list):
            a_matrix[count] = [coor[0]*coor[0], 2*coor[0]*coor[1], -2*coor[0], -2*coor[1], -1]
        return a_matrix

    def _calculate_b_matrix(self, coordinate_list):
        b_matrix = np.zeros(shape=(len(coordinate_list), 1))
        for count, coor in enumerate(coordinate_list):
            b_matrix[count] = [-coor[1]*coor[1]]
        return b_matrix

    def _calculate_least_square_result(self, a_matrix, b_matrix, edge):
        a_multiplied = np.matmul(np.transpose(a_matrix), a_matrix)
        try:
            a_inverse = np.linalg.inv(a_multiplied)
        except:
            return None
        aTbMultiplied = np.matmul(np.transpose(a_matrix), b_matrix)
        result_matrix = np.matmul(a_inverse, aTbMultiplied)
        return result_matrix

    def _calculate_center_coor_approx(self, result_matrix):
        x_approx = self._calculate_x_approx(result_matrix)
        y_approx = self._calculate_y_approx(result_matrix)
        return (x_approx, y_approx)

    def _calculate_x_approx(self, result_matrix):
        x_approx_first = result_matrix[2][0]-(result_matrix[3][0]*result_matrix[1][0])
        x_approx_second = result_matrix[0][0]-(result_matrix[1][0]*result_matrix[1][0])
        if x_approx_second != 0:
            x_approx = x_approx_first / x_approx_second
        else:
            x_approx = 9999
        return x_approx

    def _calculate_y_approx(self, result_matrix):
        y_approx_first = (result_matrix[0][0]*result_matrix[3][0])-(result_matrix[2][0]*result_matrix[1][0])
        y_approx_second = result_matrix[0][0]-(result_matrix[1][0]*result_matrix[1][0])
        if y_approx_second != 0:
            y_approx = y_approx_first / y_approx_second
        else:
            y_approx = 9999
        return y_approx

    def _filter_ellipses(self, ellipses, image):
        valid_ellipse_list = []
        for ellipse in ellipses:
            if self._ellipse_filtering(ellipse, image):
                valid_ellipse_list.append(ellipse)
        return valid_ellipse_list

    def _ellipse_filtering(self, ellipse, image):
        return  self._filter_ratio(ellipse) and \
                self._filter_error(ellipse) and \
                self._filter_size(ellipse, image.shape) and \
                self._filter_screen_border(ellipse, image.shape)

    def _filter_screen_border(self, ellipse, image_shape):
        if ellipse.center('x') - ellipse.max_size() < 0 or ellipse.center('x') + ellipse.max_size() > image_shape[1]:
            return False
        elif ellipse.center('y') - ellipse.max_size() < 0 or ellipse.center('y') + ellipse.max_size() > image_shape[0]:
            return False
        else:
            return True

    def _filter_error(self, ellipse):
        error = self._error_least_square(ellipse)
        return error < self._ellipse_error_threshold

    def _error_least_square(self, ellipse):                                     #!
        full_error = 0
        for edge_pixel in ellipse.edge_pixels():
            angle = self._calculate_ellipse_angle_from_pixel(ellipse, edge_pixel)
            ellipse_coor_1, ellipse_coor_2 = self._calculate_ellipse_coor_from_angle(ellipse, angle)
            full_error += self._calculate_minimum_ellipse_error(ellipse, [ellipse_coor_1, ellipse_coor_2])
        normalized_error = full_error / len(ellipse.edge_pixels())
        return normalized_error

    def _calculate_ellipse_angle_from_pixel(self, ellipse, edge_pixel):
        vector = [ellipse.center()[0] - edge_pixel[0], ellipse.center()[1] - edge_pixel[1]]   #Find the vector going through the coordinate and the ellipse center coordinate
        hypotenuse = math.sqrt(vector[0]**2 + vector[1]**2)                             #From now on is the center coordinates [0, 0] because of the centralization that also happens when substracting
        vector_angle = math.asin(vector[1] / hypotenuse)
        return vector_angle


    def _calculate_ellipse_coor_from_angle(self, ellipse, angle):               #!
        #Find the two places where the vector is intersecting with the ellipse, rotate them, push them back to the right center and calculate the error
        a = ellipse.width()
        b = ellipse.height()
        #Find ellipse edge coordinate based on angle
        calc_edge_coor_x_1 = (a * b) / math.sqrt(b**2 + (a**2 * math.tan(angle)**2))
        calc_edge_coor_y_1 = calc_edge_coor_x_1 * math.tan(angle)
        #Determine which Point
        if angle <= 90 or angle > 270: pass
        else:
            calc_edge_coor_x_1 =   -calc_edge_coor_x_1
            calc_edge_coor_y_1 =   -calc_edge_coor_y_1
        calc_edge_coor_x_2 = -calc_edge_coor_x_1
        calc_edge_coor_y_2 = -calc_edge_coor_y_1

        ellipse_coor_1 = (calc_edge_coor_x_1, calc_edge_coor_y_1)
        ellipse_coor_2 = (calc_edge_coor_x_2, calc_edge_coor_y_2)
        return ellipse_coor_1, ellipse_coor_2


    def _calculate_minimum_ellipse_error(self, ellipse, ellipse_coor_list):     #!
        error_list = []
        for ellipse_coor in ellipse_coor_list:
            x_rotated = math.cos(ellipse.rotation('rad')) * ellipse_coor[0] - math.sin(ellipse.rotation('rad')) * ellipse_coor[1]
            y_rotated = math.sin(ellipse.rotation('rad')) * ellipse_coor[0] + math.cos(ellipse.rotation('rad')) * ellipse_coor[1]
            x_rotated_pushed_back = x_rotated + ellipse.center()[0]
            y_rotated_pushed_back =  y_rotated + ellipse.center()[1]
            error = math.sqrt((x_rotated_pushed_back - ellipse.center()[0])**2 + (y_rotated_pushed_back - ellipse.center()[1])**2)
            error_list.append(error)
        return max(error_list)


    def _filter_ratio(self, ellipse):
        ratio =  ellipse.ratio()
        return ratio < 50 and ratio > 0.02

    def _filter_size(self, ellipse, image_size):
        return ellipse.height() < image_size[0] and ellipse.width() < image_size[1]







class EllipseFiltering:
    def __init__(self, rules):
        self.rules = rules.get_rules()

    def filter(self, ellipses):
        special_ellipses = []
        for ellipse in ellipses:
            true_list = []
            for rule in self.rules:
                if rule(ellipses,ellipse) == False: break
                else: true_list.append(True)
            if len(true_list) == len(self.rules):
                special_ellipses.append(ellipse)
        return special_ellipses







class EllipseRules:
    def get_rules():
        pass


class RobotEllipseRules(EllipseRules):
    def __init__(self, visualization_level = 0):
        self.visualization_level = 0

    def get_rules(self):
        return [self.super_sub_circle_rule, ]     #self.not_rectangle, self.differential_rule   self.quadrant_rule,

    def quadrant_rule(self, ellipses, ellipse):
        quadrant_chect_list = [0, 0, 0, 0]
        for pixel in ellipse.edge_pixels()[0::4]:
            if pixel[0] >= ellipse.center()[0] and pixel[1] >= ellipse.center()[1]:
                quadrant_chect_list[0] = 1
            elif pixel[0] < ellipse.center()[0] and pixel[1] > ellipse.center()[1]:
                quadrant_chect_list[1] = 1
            elif pixel[0] <= ellipse.center()[0] and pixel[1] <= ellipse.center()[1]:
                quadrant_chect_list[2] = 1
            elif pixel[0] > ellipse.center()[0] and pixel[1] < ellipse.center()[1]:
                quadrant_chect_list[3] = 1
        return 0 not in quadrant_chect_list

    def super_sub_circle_rule(self, ellipses, primary_ellipse):
        new_method_result = self._outside_in_corner_points(ellipses, primary_ellipse)
        return new_method_result

    def _outside_in_corner_points(self, ellipses, primary_ellipse):
        for secondary_ellipse in ellipses:
            if  EllipseHelpFunction.is_ellipse_inside_ellipse(secondary_ellipse, primary_ellipse) == True or \
                EllipseHelpFunction.is_ellipse_inside_ellipse(primary_ellipse, secondary_ellipse) == True:
                return True
        return False

    def not_rectangle(self, ellipses, ellipse):
        return True
        edge_pixels = ellipse.edge_pixels()
        ordered_edge_pixels = self._convert_to_connected_edge(edge_pixels)
        area_real = self._calculate_area_of_form(ellipse.center(), ordered_edge_pixels)
        center_angle, missing_angle = self._find_missing_angle_in_form(ellipse, ordered_edge_pixels)
        #Calculating the ideal areas for an rectangle and ellipse with the given dimensions
        full_rectangle_area = ellipse.height() * ellipse.width() * 4
        area_rectangle = self._area_of_form_minus_missing_section(ellipse.width(), ellipse.height(), missing_angle, center_angle, full_rectangle_area, self._calculate_vector_to_edge_from_angle_rectangle)
        full_ellipse_area = ellipse.height() * ellipse.width() * math.pi
        area_ellipse = self._area_of_form_minus_missing_section(ellipse.width(), ellipse.height(), missing_angle, center_angle, full_ellipse_area, self._calculate_vector_to_edge_from_angle_ellipse)
        #Determine if the form is closest to an ellipse based area
        ellipse_area_diff = abs(area_real - area_ellipse)
        rectangle_area_diff = abs(area_real - area_rectangle)
        return ellipse_area_diff < rectangle_area_diff


    def _find_missing_angle_in_form(self, ellipse, ordered_edge_pixels):
        center_pixel = ellipse.center()
        shift_rotation_RAD = ellipse.rotation('rad')
        first_pixel = ordered_edge_pixels[0]
        middle_pixel = ordered_edge_pixels[int(len(ordered_edge_pixels)/2)]
        last_pixel = ordered_edge_pixels[-1]

        vector_first = (center_pixel[0] - first_pixel[0], center_pixel[1] - first_pixel[1])
        vector_middle = (center_pixel[0] - middle_pixel[0], center_pixel[1] - middle_pixel[1])
        vector_last = (center_pixel[0] - last_pixel[0], center_pixel[1] - last_pixel[1])

        first_last_angle = self._angle_between_two_vectors(vector_first, vector_last)
        first_middle_angle = self._angle_between_two_vectors(vector_first, vector_middle)

        if first_last_angle < first_middle_angle:
            missing_angle_span_RAD = first_last_angle
        else:
            missing_angle_span_RAD = math.radians(360) - first_last_angle

        #Find missing section angles
        first_angle =  self._vector_angle(vector_first)
        last_angle = self._vector_angle(vector_last)
        center_angle = (first_angle + last_angle)/2

        #Make them relative to the local ellispe
        center_angle_relative_RAD = self._make_angle_relative(center_angle, shift_rotation_RAD)
        return center_angle_relative_RAD, missing_angle_span_RAD

    def _vector_angle(self, vector):
        x = vector[0]
        y = vector[1]
        angle = abs(math.atan(y/x))
        if x < 0: angle += math.radians(90)
        if y < 0: angle += math.radians(180)
        return angle

    def _make_angle_relative(self, angle_RAD, rotation_RAD):
        relative_angle = angle_RAD - rotation_RAD
        if relative_angle < math.radians(0): 
            relative_angle = math.radians(360) + relative_angle
        elif relative_angle > math.radians(360):
            relative_angle = relative_angle - 360
        return relative_angle


    def _dotproduct_of_two_vectors(self, v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))

    def _length_of_vector(self, v):
        return math.sqrt(self._dotproduct_of_two_vectors(v, v))

    def _angle_between_two_vectors(self, v1, v2):
        return math.acos(self._dotproduct_of_two_vectors(v1, v2) / (self._length_of_vector(v1) * self._length_of_vector(v2)))

    def _calculate_section_area_from_integral_vectors(self, integral_vectors):
        section_area = 0
        for point_nr, edge_point in enumerate(integral_vectors):
            if point_nr > 0:
                first_vector = integral_vectors[point_nr-1]
                second_vector = integral_vectors[point_nr]
                triangle_area = self._calculate_triangle_area_vectors(first_vector, second_vector)
                section_area += triangle_area
        return section_area


    def _area_of_form_minus_missing_section(self,  width, height, missing_RAD, center_angle_RAD, full_area, vector_function):
        first_RAD = center_angle_RAD - (missing_RAD / 2)
        last_RAD = center_angle_RAD + (missing_RAD / 2)

        #Find edge vectors based on section integrale
        integral_vectors = []
        starting_angle = math.floor(math.degrees(first_RAD))
        ending_angle = math.ceil(math.degrees(last_RAD))
        for angle in range(starting_angle, ending_angle+1, 1):
            edge_point_at_angle = vector_function(width, height, math.radians(angle))
            integral_vectors.append(edge_point_at_angle)

        #Find section area based on edge vectors
        section_area = self._calculate_section_area_from_integral_vectors(integral_vectors)

        #substract extra area from full area
        section_triangle_area = self._calculate_triangle_area_vectors(integral_vectors[0], integral_vectors[-1])
        substraction_area = section_area - section_triangle_area
        area = full_area - substraction_area
        return area


    def _calculate_vector_to_edge_from_angle_rectangle(self, width, height, angle):
        width_half = width
        height_half = height

        corner_angle_1 = math.atan(height_half / width_half)
        corner_angle_2 = math.atan(height_half / -width_half)
        corner_angle_3 = math.atan(-height_half / -width_half)
        corner_angle_4 = math.atan(-height_half / width_half)

        if (angle > corner_angle_1 and angle < corner_angle_2) or (angle > corner_angle_3 and angle < corner_angle_4):
            #Use height
            angle = 90-angle
            x = math.sin(angle) * (height_half / math.cos(angle))
            y = math.cos(angle) * (height_half / math.cos(angle))
        else:
            #Use width
            x = math.cos(angle) * (width_half / math.cos(angle))
            y = math.sin(angle) * (width_half / math.cos(angle))

        return (x, y)

    def _calculate_vector_to_edge_from_angle_ellipse(self, width, height, angle):
        radius_at_angle = self._calculate_ellipse_radius_at_angle(width, height, angle)
        width = math.cos(angle) * radius_at_angle
        height = math.sin(angle) * radius_at_angle
        return (width, height)

    def _calculate_ellipse_radius_at_angle(self, width, height, angle):
        return (width * height) / math.sqrt(((height**2)*(math.sin(angle)**2)) + ((width**2)*(math.cos(angle)**2)))


    def _calculate_area_of_form(self, center, ordered_edge_pixels):
        full_area = 0
        current_pixel = None
        last_pixel = ordered_edge_pixels[0]
        for pixel in ordered_edge_pixels[1:]:
            current_pixel = pixel
            triangle_area = self._calculate_triangle_area_three_point(center, current_pixel, last_pixel)
            full_area += triangle_area
            last_pixel = current_pixel
        current_pixel = ordered_edge_pixels[0]
        triangle_area = self._calculate_triangle_area_three_point(center, current_pixel, last_pixel)
        full_area += triangle_area
        return full_area


    def _calculate_triangle_area_three_point(self, point_a, point_b, point_c):
        #Get two vectors from points
        vector_a = (abs(point_a[0] - point_b[0]), abs(point_a[1] - point_b[1]))
        vector_b = (abs(point_a[0] - point_c[0]), abs(point_a[1] - point_c[1]))
        vector_a_np = np.asarray(vector_a)
        vector_b_np = np.asarray(vector_b)
        triangle_area = self._calculate_triangle_area_vectors(vector_a_np, vector_b_np)
        return triangle_area

    def _calculate_triangle_area_vectors(self, vec_a, vec_b):
        #Calculate rectangle area with cross-product
        cross_product = np.cross(vec_a, vec_b)
        full_area = np.linalg.norm(cross_product)
        #Half of area gives an triangle
        triangle_area = full_area / 2
        return triangle_area


    def _length_between_points(self, point_a, point_b):
        x_diff = abs(point_a[0] - point_b[0])
        y_diff = abs(point_a[1] - point_b[1])
        length = x_diff if x_diff > y_diff else y_diff
        return length


    def _find_list_to_connect(self, list_of_lists, sub_list, index_nr = -1):
        index = -1
        flags = { 'reverse': 0, 'order': 1 }
        for index_count, list in enumerate(list_of_lists):
            if index_count != index_nr:
                first_px_of_list = list[0]
                last_px_of_list = list[-1]
                first_px_of_sub = sub_list[0]
                last_px_of_sub = sub_list[-1]

                if self._length_between_points(first_px_of_list, first_px_of_sub) == 1:
                    flags['reverse'] = 1
                    flags['order'] = 1
                    index = index_count
                    break
                elif self._length_between_points(first_px_of_list, last_px_of_sub) == 1:
                    flags['reverse'] = 0
                    flags['order'] = 2
                    index = index_count
                    break
                elif self._length_between_points(last_px_of_list, first_px_of_sub) == 1:
                    flags['reverse'] = 0
                    flags['order'] = 1
                    index = index_count
                    break
                elif self._length_between_points(last_px_of_list, last_px_of_sub) == 1:
                    flags['reverse'] = 2
                    flags['order'] = 1
                    index = index_count
                    break

        return index, flags

    def _convert_to_connected_edge(self, ordered_edge):
        ordered_edge_list = ordered_edge
        ordered_edge_list.append((999999, 999999))

        list_of_lists = [[ordered_edge_list[0]]]
        sub_list = [ordered_edge_list[1]]                        #Sub connected graph / link / connections

        for pixel in ordered_edge_list[1:]:
            length = self._length_between_points(pixel, sub_list[-1])
            if length == 1:
                sub_list.append(pixel)
            if length > 1:
                index, end_flags = self._find_list_to_connect(list_of_lists, sub_list)
                if index == -1: list_of_lists.append(sub_list)
                else:
                    if end_flags['reverse'] == 1:
                        list_of_lists[index].reverse()
                    elif end_flags['reverse'] == 2:
                        sub_list.reverse()
                    if end_flags['order'] == 1:
                        list_of_lists[index].extend(sub_list)
                    elif end_flags['order'] == 2:
                        sub_list.extend(list_of_lists[index])
                        list_of_lists[index] = sub_list

                    old_index = index
                    new_index, end_flags = self._find_list_to_connect(list_of_lists, list_of_lists[old_index], old_index)
                    if new_index != -1:
                        if end_flags['reverse'] == 1:
                            list_of_lists[new_index].reverse()
                        elif end_flags['reverse'] == 2:
                            list_of_lists[old_index].reverse()
                        if end_flags['order'] == 1:
                            list_of_lists[new_index].extend(list_of_lists[old_index])
                            del list_of_lists[old_index]
                        elif end_flags['order'] == 2:
                            list_of_lists[old_index].extend(list_of_lists[new_index])
                            del list_of_lists[new_index]
                sub_list = [pixel]

        return list_of_lists[0]















class EllipseHelpFunction:
    def is_ellipse_inside_ellipse(inner_ellipse, outer_ellipse):
        length_between_centers = EllipseHelpFunction.length_between_centers(outer_ellipse.center(), inner_ellipse.center())
        if outer_ellipse != inner_ellipse and (length_between_centers < outer_ellipse.max_size() or length_between_centers < inner_ellipse.max_size()):
            primary_corner_coor = EllipseHelpFunction.calculate_ellipse_corner_coors(outer_ellipse)
            secondary_corner_coor = EllipseHelpFunction.calculate_ellipse_corner_coors(inner_ellipse)
            if  EllipseHelpFunction.check_if_points_is_inside_ellipse(outer_ellipse, secondary_corner_coor):
                return True
        return False

    def calculate_vector_to_edge_from_angle(ellipse, angle):
        radius_at_angle = EllipseHelpFunction._calculate_ellipse_radius_at_angle(ellipse, angle)
        width = math.cos(angle) * radius_at_angle
        height = math.sin(angle) * radius_at_angle
        return (width, height)

    def calculate_radius_from_vector(ellipse, vector, distance):
        normalized_vector = (vector[0]/distance, vector[1]/distance)
        angle = EllipseHelpFunction._calculate_angle_from_vector(ellipse, normalized_vector)
        radius = EllipseHelpFunction._calculate_ellipse_radius_at_angle(ellipse, angle)
        return radius

    def _calculate_ellipse_radius_at_angle(ellipse, angle):
        return (ellipse.width() * ellipse.height()) / math.sqrt(((ellipse.height()**2)*(math.sin(angle)**2)) + ((ellipse.width()**2)*(math.cos(angle)**2)))

    def _calculate_angle_from_vector(ellipse, normalized_vector):
        vector_angle = math.asin(normalized_vector[1])
        angle = vector_angle + ellipse.rotation('rad')
        return angle

    def length_between_centers(center_a, center_b):
        width_diff = center_b[0] - center_a[0]
        height_diff = center_b[1] - center_a[1]
        length_between_centers = math.sqrt(width_diff**2 + height_diff**2)
        return length_between_centers

    def calculate_ellipse_corner_coors(ellipse):
        width_angle_RAD = ellipse.rotation('rad')
        height_angle_RAD = abs(width_angle_RAD - math.radians(90))
        point_one, point_two = EllipseHelpFunction._calc_point_from_point_with_vector(ellipse.center(), ellipse.width(), width_angle_RAD)
        point_three, point_four = EllipseHelpFunction._calc_point_from_point_with_vector(ellipse.center(), ellipse.height(), height_angle_RAD)
        return [point_one, point_two, point_three, point_four]

    def _calc_point_from_point_with_vector(center, hypotenuse, angle):
        width_tri = math.cos(angle) * hypotenuse
        height_tri = math.sin(angle) * hypotenuse
        point_one = (center[0] + width_tri,  center[1] + height_tri)
        point_two = (center[0] - width_tri,  center[1] - height_tri)
        return point_one, point_two

    def check_if_points_is_inside_ellipse(ellipse, points):
        direction_vectors = EllipseHelpFunction._calculate_vector_between_one_coor_to_many(ellipse.center(), points)
        return EllipseHelpFunction._vector_inside_of_ellipse(ellipse, direction_vectors)

    def _vector_inside_of_ellipse(ellipse, direction_vectors):
        for dir_vec in direction_vectors:
            direction_lengt = math.sqrt(dir_vec[0]**2 + dir_vec[1]**2)
            radius_at_vector = EllipseHelpFunction.calculate_radius_from_vector(ellipse, dir_vec, direction_lengt)
            if direction_lengt > radius_at_vector:
                return False
        return True

    def _calculate_vector_between_one_coor_to_many(primary_center, center_list):
        vector_list = []
        for center in center_list:
            width_diff = center[0] - primary_center[0]
            height_diff = center[1] - primary_center[1]
            new_vector = (width_diff, height_diff)
            vector_list.append(new_vector)
        return vector_list










#Nothing
