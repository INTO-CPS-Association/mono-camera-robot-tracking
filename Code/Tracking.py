import numpy as np
from sympy import *


class RobotTracking:
    def __init__(self, circle_resources, robot_resources):
        self.circle_resouces = circle_resources
        self.robot_resources = robot_resources

    def get_positions(self, camera, frame, robot_set):
        robot_ellipse_map = self._split_ellipses_into_robots(ellipses)
        robot_positions = []
        for robot_id in robot_ellipse_map:
            robot_vectors = self._vectors_to_robot_from_cam(robot_ellipse_map, robot_id)
            center_pixel = self._center_pixel(robot_set, robot, robot_vectors)
            distance_to_center = np.linalg.norm(robot_vectors['center'])

            angle_to_center_pixel_floor = self._angle_to_pixel_floor(camera, center_pixel)
            expected_distance_to_center = self._expected_distance_to_pixel(camera, center_pixel)
            angle_to_center_pixel_cam = self._angle_to_pixel_cam(camera, expected_distance_to_center)

            robot_position_local = self._find_robot_position_local(cam, angle_to_center_pixel_floor, angle_to_center_pixel_cam, expected_distance_to_center, distance_to_center)
            robot_position_global = self._find_robot_position_gobal(cam, robot_position_local)

            robot_positions.append(robot_position_global)
        return robot_positions


    def _split_ellipses_into_robots(self, ellipses):
        robot_sets = {}
        for ellipse in ellipses:
            ellipse_id = ellipse.get_id()
            robot_id = self.circle_resouces.get_model_by_id(ellipse_id)
            if robot_id not in robot_sets:
                robot_set[robot_id] = []
            robot_set[robot_id].append(ellipse)
        return robot_sets

    def _vectors_to_robot_from_cam(self, robot_ellipse_map, robot_id):
        #---------------Setup---------------
        ellipse_ids = [robot_ellipse_map[robot_id][index].get_id() for index in range(0, len(robot_ellipse_map[robot_id]))]
        circle_numbers = [self.circle_resouces.get_circle_number_by_id(ellipse_id) for ellipse_id in ellipse_ids]

        circle_pos_1 = self.robot_resources.get_circle_placement_by_id(robot_id, circle_numbers[0])
        circle_pos_2 = self.robot_resources.get_circle_placement_by_id(robot_id, circle_numbers[1])
        circle_pos_3 = self.robot_resources.get_circle_placement_by_id(robot_id, circle_numbers[2])

        robot_center = self.robot_resources.get_robot_center_by_id(robot_id)
        center_vector = np.asarray(robot_center)

        vector_a = self._points_to_vector(circle_pos_1, circle_pos_2)
        vector_b = self._points_to_vector(circle_pos_1, circle_pos_3)

        #----------Scaling value-----------
        orthogonal_vector = np.cross(vector_a, vector_b)

        combined_vectors = np.array([vector_a, vector_b, orthogonal_vector, center_vector])
        matrix = Matrix(combined_vectors.T)

        m_rref = matrix.rref()
        scaling_values = m_rref.col(-1)

        #---------Distance vectors---------
        d1 = robot_ellipse_map[robot_id][0].get_distance()
        d2 = robot_ellipse_map[robot_id][1].get_distance()
        d3 = robot_ellipse_map[robot_id][2].get_distance()

        e1e2_local_vec = np.asarray(circle_pos_2) - np.asarray(circle_pos_1)
        e1e3_local_vec = np.asarray(circle_pos_3) - np.asarray(circle_pos_1)
        e2e3_local_vec = np.asarray(circle_pos_3) - np.asarray(circle_pos_2)

        e1e2_dist = np.linalg.norm(e1e2_local_vec)
        e1e3_dist = np.linalg.norm(e1e3_local_vec)
        e2e3_dist = np.linalg.norm(e2e3_local_vec)

        v0 = math.acos((d1**2 + d2**2 - e1e2_dist**2)/(2 * d1 * d2))
        v1 = math.acos((d1**2 + e1e2_dist**2 - d2**2)/(2 * d1 * e1e2_dist))

        he = e1e2_dist * math.sin(math.acos((e1e2_dist**2 + e1e3_dist**2 - e2e3_dist**2)/(2 * e1e2_dist * e1e3_dist)))

        l_x = math.sqrt(e1e3_dist**2 - he**2)
        x_he = he * math.cos(math.acos((x**2 + he**2 - d3**2)/(2 * x * he)))

        hx = math.sin(v1)*l_x
        v_xh = math.atan(hx/(d1 - math.cos(v1)*l_x))

        x = math.sqrt((d1 - math.cos(v1)*l_x)**2 + hx**2)

        d1_vec = np.array([d1, 0, 0])
        d2_vec = np.array([d2 * math.cos(v0), d2 * math.sin(v0), 0])
        d3_vec = np.array([(x - x_he) * math.cos(v_xh), (x - x_he) * math.sin(v_xh), math.sqrt(he**2 - x_he**2)])

        #----------Ellipse vectors----------
        e1e2_vec = d2_vec - d1_vec
        e1e3_vec = d3_vec - d1_vec
        e2e3_vec = d3_vec - d2_vec

        #----Vec from ellipse to center----
        e1e2_e1e3_orthogonal_vec = np.cross(e1e2_vec, e1e3_vec)
        e1center_vec = scaling_values[0] * e1e2_vec + scaling_values[1] * e1e3_vec + scaling_values[2] * e1e2_e1e3_orthogonal_vec

        #-----distance to robot center-----
        cam_center_vec = d1_vec + e1center_vec

        #--------------Return--------------
        return {'center': center_vec, 'circles': [{'vec': d1_vec, 'id': ellipse_ids[0]}, {'vec': d2_vec, 'id': ellipse_ids[1]}, {'vec': d3_vec, 'id': ellipse_ids[2]}]}

    def _points_to_vector(self, point_a, point_b):
        np_a = np.asarray(point_a)
        np_b = np.asarray(point_b)
        np_c = np_a - np_b
        return np_c


    def _center_pixel(self, robot_set, robot, robot_vectors):
        #Redefiners plane
        x = 1
        y = 2
        z = 0

        #Unpack vectors
        cam_center_vec = robot_vectors['center']
        ellipse_1_vec = robot_vectors['circles'][0]
        ellipse_2_vec = robot_vectors['circles'][1]
        ellipse_3_vec = robot_vectors['circles'][2]

        #Get pixel coordinates
        ellipse_1_px = robot_set[0].get_center()
        ellipse_2_px = robot_set[1].get_center()
        ellipse_3_px = robot_set[2].get_center()

        #Center vector
        l_x = ellipse_1_vec[x] + ellipse_2_vec[x] + ellipse_3_vec[x]
        l_y = ellipse_1_vec[y] + ellipse_2_vec[y] + ellipse_3_vec[y]
        l_z = ellipse_1_vec[z] + ellipse_2_vec[z] + ellipse_3_vec[z]
        center_vec = np.array([0, 0, 0])
        center_vec[x] = lx / 3; center_vec[y] = ly / 3; center_vec[z] = lz / 3

        #Find rotation of center_vec
        v1 = math.atan(center_vec[x] / center_vec[y])
        v2 = math.atan(center_vec[z] / math.sqrt(center_vec[x]**2 + center_vec[z]))

        #Rotate robot vectors
        ellipse_1_vec_new = self._rotate_around_y_axis(ellipse_1_vec, v1, [x, y, z])
        ellipse_1_vec_new = self._rotate_around_x_axis(ellipse_1_vec, v2, [x, y, z])

        ellipse_2_vec_new = self._rotate_around_y_axis(ellipse_2_vec, v1, [x, y, z])
        ellipse_2_vec_new = self._rotate_around_x_axis(ellipse_2_vec, v2, [x, y, z])

        ellipse_3_vec_new = self._rotate_around_y_axis(ellipse_3_vec, v1, [x, y, z])
        ellipse_3_vec_new = self._rotate_around_x_axis(ellipse_3_vec, v2, [x, y, z])

        cam_to_center_vec_new = self._rotate_around_y_axis(cam_center_vec, v1, [x, y, z])
        cam_to_center_vec_new = self._rotate_around_x_axis(cam_center_vec, v2, [x, y, z])

        #Shift each pixel
        ellipse_1_vec_shifted = ellipse_1_vec_new - ellipse_1_vec_new
        ellipse_2_vec_shifted = ellipse_2_vec_new - ellipse_1_vec_new
        ellipse_3_vec_shifted = ellipse_3_vec_new - ellipse_1_vec_new
        cam_to_center_vec_shifted = cam_to_center_vec_new - ellipse_1_vec_new

        #Find vectors
        a_vec = np.array([ellipse_2_vec_shifted[x], ellipse_2_vec_shifted[y]])
        b_vec = np.array([ellipse_3_vec_shifted[x], ellipse_3_vec_shifted[y]])
        c_vec = np.array([cam_to_center_vec_shifted[x], cam_to_center_vec_shifted[y]])

        #Find scale factors
        combined_vectors = np.array([a_vec, b_vec, c_vec])
        matrix = Matrix(combined_vectors.T)
        m_rref = matrix.rref()
        scaling_values = m_rref.col(-1)

        #Make pixel vectors
        vec_a_px = np.array([ellipse_2_px[0] - ellipse_1_px[0], ellipse_2_px[1] - ellipse_1_px[1]])
        vec_b_px = np.array([ellipse_3_px[0] - ellipse_1_px[0], ellipse_3_px[1] - ellipse_1_px[1]])

        #Find center pixel
        center_pixel_vec = scaling_values[0] * vec_a_px + scaling_values[1] * vec_b_px
        center_px = (int(center_pixel_vec[0]), int(center_pixel_vec[1]))
        center_px_shifted = (center_px[0] + ellipse_1_px[0], center_px[1] + ellipse_1_px[1])

        return center_px_shifted



    def _rotate_around_y_axis(vec, angle, plane_rotation):
        new_vec = vec.copy()
        new_vec[plane_rotation[0]] = vec[plane_rotation[0]] * math.cos(angle) + vec[plane_rotation[2]] * math.sin(angle)
        new_vec[plane_rotation[1]] = vec[plane_rotation[1]]
        new_vec[plane_rotation[2]] = vec[-plane_rotation[0]] * math.sin(angle) + vec[plane_rotation[2]] * math.cos(angle)
        return new_vec

    def _rotate_around_x_axis(vec, angle, plane_rotation):
        new_vec = vec.copy()
        new_vec[plane_rotation[0]] = vec[plane_rotation[0]]
        new_vec[plane_rotation[1]] = vec[plane_rotation[1]] * math.cos(angle) - vec[plane_rotation[2]] * math.sin(angle)
        new_vec[plane_rotation[2]] = vec[plane_rotation[0]] * math.sin(angle) + vec[plane_rotation[2]] * math.cos(angle)
        return new_vec


    def _angle_to_pixel_floor(self, camera, pixel):
        X_p = pixel[0] / camera.get_frame_size('x')
        Y_p = pixel[1] / camera.get_frame_size('y')

        if X_p > 0.5:
            X_p = 1 - X_p
        if Y_p > 0.5:
            Y_p = 1 - Y_p

        v_HY = (camera.get_horizontal_view_degrees('rad') / 2) - camera.get_horizontal_view_degrees('rad') * Y_p
        v_VX = camera.get_vertical_view_degrees('rad') * X_p

        d3 = math.sin(camera.get_angle_to_floor('rad')-(camera.get_vertical_view_degrees('rad')/2)) * (camera.get_position()[2]/(math.cos(camera.get_angle_to_floor('rad')-(camera.get_vertical_view_degrees('rad')/2))))
        d5 = math.sin(v_HY) * (d3/math.cos(v_HY))

        d6 = (d5/math.sin(v_HY)) * math.tan(v_HY)
        d7 = sqrt((d1-math.cos(v_VX)*d6)**2 + (math.sin(v_VX)*d6)**2)

        angle_to_pixel_floor = math.atan(d5 / (d7 + d3))
        return angle_to_pixel_floor


    def _angle_to_pixel_cam(self, camera, length_to_pixel):
        return math.atan(length_to_pixel / camera.get_height())

    def _expected_distance_to_pixel(self, camera, pixel):
        X_p = pixel[0] / camera.get_frame_size('x')
        Y_p = pixel[1] / camera.get_frame_size('y')

        if X_p > 0.5:
            X_p = 1 - X_p
        if Y_p > 0.5:
            Y_p = 1 - Y_p

        v_HY = (camera.get_horizontal_view_degrees('rad') / 2) - camera.get_horizontal_view_degrees('rad') * Y_p
        v_VX = camera.get_vertical_view_degrees('rad') * X_p

        d3 = math.sin(camera.get_angle_to_floor('rad')-(camera.get_vertical_view_degrees('rad')/2)) * (camera.get_position()[2]/(math.cos(camera.get_angle_to_floor('rad')-(camera.get_vertical_view_degrees('rad')/2))))
        d5 = math.sin(v_HY) * (d3/math.cos(v_HY))

        d6 = (d5/math.sin(v_HY)) * math.tan(v_HY)
        d7 = sqrt((d1-math.cos(v_VX)*d6)**2 + (math.sin(v_VX)*d6)**2)

        direct_length_floor = math.sqrt((d7 + d3)**2 + d5**2)
        direct_length = sqrt(camera.get_height()**2 + direct_length_floor)
        return direct_length


    def _find_robot_position_local(self, camera, floor_angle, cam_angle, expected_distance, actual_distance):
        dr = expected_distance - actual_distance
        cam_angle_inverse = 90 - cam_angle

        le = math.sqrt(expected_distance**2 - camera.get_height())
        lr = math.cos(cam_angle_inverse) * dr
        la = le - lr

        hd = math.sin(floor_angle) * la
        ld = math.cos(floor_angle) * la
        ha = math.sin(cam_angle_inverse) * dr

        x = ld; y = hd; z = ha      #x, y - Will make the vector
        return {'x': x, 'y': y, 'height': z}


    def _find_robot_position_gobal(self, camera, local_position):
        a_vec = np.array([camera.get_position('x'), camera.get_position('y'), camera.get_position('z')])

        angle_robot_local = math.atan(local_position['x']/local_position['y'])
        angle_camera_global = camera.get_rotation('rad')
        angle_robot_global = angle_robot_local - angle_camera_global

        b_vec_x = math.cos(angle_robot_global) * robot_vector_length
        b_vec_y = math.sin(angle_robot_global) * robot_vector_length
        b_vec_z = local_position['z']
        b_vec = np.array([b_vec_x, b_vec_y])

        global_robot_vec = a_vec + b_vec
        return global_robot_vec





















#Nothing
