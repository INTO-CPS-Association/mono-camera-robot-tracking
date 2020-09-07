from Models.CameraModels import CameraInfo

class RobotResources:
    def __init__(self):
        self.robots = { '1': {
                            'dimensions': (47.0, 34.5, 22.5),
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


class CircleResources:
    def __init__(self):
        self.circles = {3:  { 'type': 'calibration',  'model': 'floor_gang', 'locked_coordinate': (0, 0, 0), 'size': 145 }, \
                        5:  { 'type': 'calibration', 'model': 'floor_gang', 'locked_coordinate': (400, 250, 0), 'size': 145 },  \
                        7:  { 'type': 'calibration', 'model': 'floor_gang', 'locked_coordinate': (0, 500, 0), 'size': 145 }, \
                        4:  { 'type': 'robot', 'model': '1', 'circle_number': '1', 'size': 145 }, \
                        6:  { 'type': 'robot', 'model': '1', 'circle_number': '2', 'size': 145 }, \
                        8:  { 'type': 'robot', 'model': '1', 'circle_number': '3', 'size': 145 }, \
                        9:  { 'type': 'robot', 'model': '1', 'circle_number': '5', 'size': 145 }, \
                        10: { 'type': 'robot', 'model': '1', 'circle_number': '4', 'size': 145 } }

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


    def valid_id(self, id):
        return id in self.circles



class CameraInfoRecouces:
    def __init__(self):
        self._camera_properties = {
            'GEA': { 'view_degrees_horizontal': 80 },
            'Logitech-C210': { 'view_degrees_vertical': 26.14 },
            'GoPro-Hero6': {},
            'Lenevo': { 'view_degrees_horizontal': 60 }
        }

    def get_camInfo_properties_by_name(self, name):
        return self._camera_properties[name]

    def get_names(self):
        return list(self._camera_properties.keys())

















#Nothing
