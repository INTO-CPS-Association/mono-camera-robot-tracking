import random
import math
import cv2



class Ellipse:
    def __init__(self, edge_pixels, center, width, height, rotation):
        self._height = height
        self._width = width
        self._center = center   #x, y
        self._rotation = rotation
        self._edge_pixels = edge_pixels
        self._id = random.randint(0,1000000000)

    def __eq__(self, secondary_ellipse):
        if isinstance(secondary_ellipse, Ellipse):
            return self.id() == secondary_ellipse.id()
        return False

    def height(self):
        return self._height

    def width(self):
        return self._width

    def max_size(self):
        return self.height() if self.height() > self.width() else self.width()

    def min_size(self):
        return self.height() if self.height() < self.width() else self.width()

    def ratio(self):
        return self.max_size() / self.min_size()

    def center(self, type = ''):                                                #!
        if type == '': return self._center
        elif type.lower() == 'x': return self._center[0]
        elif type.lower() == 'y': return self._center[1]
        else: return self._center

    def rotation(self, type = 'deg'):
        if type.lower() == 'deg': return self._rotation
        elif type.lower() == 'rad': return math.radians(self._rotation)
        else: return self._rotation

    def edge_pixels(self):
        return self._edge_pixels

    def id(self):
        return self._id

    def print(self):
        print("Ellipse: " + str(self.id()))
        print("    Center: " + str(self.center()))
        print("    Height: " + str(self.height()))
        print("    Width: " + str(self.width()))
        print("    Rotation: " + str(self.rotation()))
        print("    Nr. of Px.: " + str(len(self.edge_pixels())))



class RobotEllipse:
    def __init__(self, super_ellipse = None, sub_ellipses = None):
        self.super_ellipse = super_ellipse
        self.sub_ellipses = []
        self.angle = 0
        self.distance = 0
        if sub_ellipses != None:
            self.sub_ellipses = sub_ellipses

    def get_width(self):
        return self.super_ellipse.width()

    def get_height(self):
        return self.super_ellipse.height()

    def get_max_size(self):
        return self.super_ellipse.max_size()

    def get_min_size(self):
        return self.super_ellipse.min_size()

    def get_ratio(self):
        return self.super_ellipse.min_size() / self.super_ellipse.max_size()

    def get_rotation(self, type = 'deg'):
        return self.super_ellipse.rotation(type)

    def get_center(self, type = ''):
        return self.super_ellipse.center(type)

    def get_super_ellipse(self):
        return self.super_ellipse

    def get_sub_ellipses(self):
        return self.sub_ellipses

    def add_sub_ellipse(self, ellipse):
        self.sub_ellipses.append(ellipse)

    def get_id(self):
        return len(self.sub_ellipses)

    def valid(self):
        return len(self.sub_ellipses) > 0

    def set_angle(self, angle, type = 'deg'):
        if type.lower() == 'deg': self.angle = angle
        elif type.lower() == 'rad': self.angle = math.radians(angle)
        else: self.angle = angle

    def get_angle(self, type = 'deg'):
        if self.angle == None:
            return -1
        if type.lower() == 'deg': return self.angle
        elif type.lower() == 'rad': return math.radians(self.angle)
        else: return self.angle

    def set_distance(self, distance):
        self.distance = distance

    def get_distance(self):
        if self.distance == None:
            return -1
        return self.distance

    def print(self):
        self.super_ellipse.print()
        print("    Angle: " + str(self.get_angle()))
        print("    Distance: " + str(self.get_distance()))
        print("    Circle number: " + str(self.get_id()))
