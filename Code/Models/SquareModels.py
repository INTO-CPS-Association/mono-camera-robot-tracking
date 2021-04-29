class RobotSquare:
    def __init__(self, square, distance = None, angle = None, id = None):
        self._square = square
        self._angle = angle
        self._distance = distance
        self._id = id
        self._corners = None
        self._center = None
        self._setup(square)

    def _setup(self, square):
        if self._id is None:
            self._id = square["id"]
        self._corners = square["corners"]
        self._center = square["center"]

    def get_center(self, type = ''):
        if type == '': return self._center
        elif type.lower() == 'x': return self._center[0]
        elif type.lower() == 'y': return self._center[1]
        else: return self._center

    def get_id(self):
        return self._id

    def valid(self):
        return self._id > 0

    def set_angle(self, angle, type = 'deg'):
        if type.lower() == 'deg': self._angle = angle
        elif type.lower() == 'rad': self._angle = math.radians(angle)
        else: self._angle = angle

    def get_angle(self, type = 'deg'):
        if self._angle == None:
            return -1
        if type.lower() == 'deg': return self._angle
        elif type.lower() == 'rad': return math.radians(self._angle)
        else: return self._angle

    def set_distance(self, distance):
        self._distance = distance

    def get_distance(self):
        if self._distance == None:
            return -1
        return self._distance

    def get_corners(self):
        return self._corners

    def print(self):
        print("ID: " + str(self._id))
        print("Corners: " + str(self._corners))
        print("Center: " + str(self._center))
        print("Angle: " + str(self._angle))
        print("Distance: " + str(self._distance))
