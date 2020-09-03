import math


class CameraInformationHelpTool:
    def get_viewing_angle_height(objects_height, length_from_the_camera):
        return CameraInformationHelpTool_calculate_isoscele_triangle_angle(objects_height, length_from_the_camera)

    def get_viewing_angle_width(objects_width, length_from_the_camera):
        return CameraInformationHelpTool._calculate_isoscele_triangle_angle(objects_width, length_from_the_camera)

    def _calculate_isoscele_triangle_angle(height, width):
        triangle_height = height / 2
        triangle_width = width
        right_triangle_angle = CameraInformationHelpTool._calculate_right_triangle_angle(triangle_height, triangle_width)
        isoscele_triangle_angle = right_triangle_angle * 2
        return isoscele_triangle_angle

    def _calculate_right_triangle_angle(height, width):
        return math.degrees(math.atan(height/width))

    