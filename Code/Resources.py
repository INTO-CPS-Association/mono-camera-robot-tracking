from Models.CameraModels import CameraInfo

class RobotResources:
    def __init__(self):
        self.robots = { '1': {
                            'dimensions': (47.0, 34.5, 22.5),
                            'center': (23.5, 17.25, 11.25),
                            'circles': {
                                '1': { 'surface': 'front', 'position_center': (0.0, 17.25, 11.25) },
                                '2': { 'surface': 'left', 'position_center': (23.5, 0.0, 11.25) },
                                '3': { 'surface': 'right', 'position_center': (23.5, 34.5, 11.25) },
                                '4': { 'surface': 'back', 'position_center': (47.0, 17.25, 11.25) },
                                '5': { 'surface': 'top', 'position_center': (23.5, 17.25, 22.5) } }
                       } }

    def get_by_id(self, robot_id):
        return self.robots[robot_id]

    def get_circle_by_id_and_circle_number(self, robot_id, cirlce_number):
        return self.robots[robot_id]['circles'][circle_number]

    def get_dimensions_by_id(self, robot_id):
        return self.robots[robot_id]['dimensions']

    def get_circle_placement_by_id(self, robot_id, circle_number):
        return self.robots[robot_id]['circles'][circle_number]['position_center']

    def get_all_robot_ids(self):
        ids = [key for key in self.robots]
        return ids

    def get_robot_center_by_id(self, robot_id):
        return self.robots[robot_id]['center']


class CircleResources:
    def __init__(self):
        self.circles = {1:  { 'type': 'calibration',  'model': 'floor_gang', 'locked_coordinate': (1000, 150, 0), 'size': 62 }, \
                        4:  { 'type': 'calibration', 'model': 'floor_gang', 'locked_coordinate': (500, 400, 0), 'size': 62 },  \
                        7:  { 'type': 'calibration', 'model': 'floor_gang', 'locked_coordinate': (750, 800, 0), 'size': 62 }, \
                        3:  { 'type': 'robot', 'model': '1', 'circle_number': '1', 'size': 62 }, \
                        6:  { 'type': 'robot', 'model': '1', 'circle_number': '2', 'size': 62 }, \
                        8:  { 'type': 'robot', 'model': '1', 'circle_number': '3', 'size': 62 }, \
                        9:  { 'type': 'robot', 'model': '1', 'circle_number': '5', 'size': 62 }, \
                        10: { 'type': 'robot', 'model': '1', 'circle_number': '4', 'size': 62 } }

    def get_by_id(self, id):
        return self.circles[id]

    def get_type_by_id(self, id):
        return self.get_by_id(id)['type']

    def get_size_by_id(self, id):
        if 'size' in self.get_by_id(id):
            return self.get_by_id(id)['size']
        else:
            raise Exception("No size-type for the 'type'='robot' ellipses. Try with an 'type'='calibration' ellipse instead")

    def get_coordiante_by_id(self, id):
        if 'locked_coordinate' in self.get_by_id(id):
            return self.get_by_id(id)['locked_coordinate']
        else:
            raise Exception("No locked_coordinate-type for the 'type'='robot' ellipses. Try with an 'type'='calibration' ellipse instead")

    def get_model_by_id(self, id):
        if 'model' in self.get_by_id(id):
            return self.get_by_id(id)['model']
        else:
            raise Exception("No model-type for this id. This is probably an error with the resouce")

    def get_circle_number_by_id(self, id):
        if 'circle_number' in self.get_by_id(id):
            return self.get_by_id(id)['circle_number']
        else:
            raise Exception("No 'circle_number'-type for the 'type'='calibration' ellipses. Try with an 'type'='robot' ellipse instead")

    def valid_id(self, id):
        return id in self.circles



class CameraInfoResouces:
    def __init__(self):
        self._camera_properties = {
            'GEA': { 'view_degrees_horizontal': 80 },
            'Logitech-C210': { 'view_degrees_vertical': 26.14},
            'GoPro-Hero6': {},
            'Lenevo': { 'view_degrees_horizontal': 60, 'view_degrees_vertical': 40 }
        }

    def get_camInfo_properties_by_name(self, name):
        return self._camera_properties[name]

    def get_names(self):
        return list(self._camera_properties.keys())

















#Nothing
