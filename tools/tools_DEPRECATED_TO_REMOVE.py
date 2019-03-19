#!/usr/bin/env python

# tools.py
import cv2
import glob
import datetime
import numpy as np
from ..pathsandnames import PathsAndNames

class PiCameraOperations():
    @staticmethod
    def _scale():
        """
        Scale the input resolution to the ROI resolution
        :return: vector two points of a Box
        DEPRECATED
        """
        scale_factor_in_X = (PathsAndNames.segundoPunto[0] - PathsAndNames.primerPunto[0])
        scale_factor_in_Y = (PathsAndNames.segundoPunto[1] - PathsAndNames.primerPunto[1])
        return scale_factor_in_X, scale_factor_in_Y

    @staticmethod
    def _scaleLow():
        """
        Scale the input resolution to the ROI resolution
        :return: vector two points of a Box
        DEPRECATED
        """
        scale_factor_in_X = (PathsAndNames.segundoPunto[0]//4 - PathsAndNames.primerPunto[0]//4)
        scale_factor_in_Y = (PathsAndNames.segundoPunto[1]//4 - PathsAndNames.primerPunto[1]//4)
        return scale_factor_in_X, scale_factor_in_Y

    @staticmethod
    def ROI(w=0, h=0):
        """
        Retrieves or sets the crop applied to the camera’s input.

        When queried, this ROI property returns a (x, y, w, h)
        tuple of floating point values ranging from 0.0 to 1.0,
        indicating the proportion of the image to include in the output.
        The default value is (0.0, 0.0, 1.0, 1.0) which indicates that everything should be included.

        :param w: Original Wight of Image
        :param h: Original Height of Image
        :return: (x,y,w,h) array of floating points
        """

        p0x = PathsAndNames.primerPunto[0] / w
        p0y = PathsAndNames.primerPunto[1] / h

        p1x = PathsAndNames.segundoPunto[0] / w
        p1y = PathsAndNames.segundoPunto[1] / h

        return (p0x, p0y, p1x, p1y)

    @staticmethod
    def get_actual_time():
        """
        Return actual in call time in plain format to miliseconds level

        :return: actual datetimeObject, actual dateTimeObject as string format
        """
        actual_datetime = datetime.datetime.now()
        _date_string = actual_datetime.strftime('%Y%m%d_%H%M%S_%f')[:-4]
        actual_datetime_array = (actual_datetime.year,
                         actual_datetime.month,
                         actual_datetime.day,
                         actual_datetime.hour,
                         actual_datetime.minute,
                         actual_datetime.second, actual_datetime.microsecond)

        return actual_datetime_array, _date_string


if __name__ == '__main__':
    pass
