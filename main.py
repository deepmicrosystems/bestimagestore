#!/usr/bin/env python3

import os
import cv2
import argparse
import datetime

from highresolutionrecorder import HighResolutionRecorder

parser = argparse.ArgumentParser(description = 'Settings configurations for the shutter class')
parser.add_argument('-W', '--width',  type = int,  default = '2560', help = 'Widht of the picture')
parser.add_argument('-H', '--heigth', type = int,  default = '1920', help = 'Heigth of the picture in pixels')
parser.add_argument('-r', '--roi',    type = bool, default = False,  help = 'Enable ROI')
parser.add_argument('-s', '--show',   type = bool, default = False,  help = 'Show frames in real time')
#parser.add_argument('-s', '--save',   type = bool, default = False,  help = 'Save all low resolution frames')
args = parser.parse_args()

myRecorder = HighResolutionRecorder(width = 2560,
                                    height = 1920,
                                    simulation = True,          # False
                                    apply_roi = False,
                                    apply_background = False,
                                    save_low_resolution = False,
                                    trafficlight = None)

if __name__ == "__main__":
    while True:
        image = myRecorder.process_new_image()
        ch = cv2.waitKey(1)
        if args.show:
            cv2.imshow('Display', image)
        if ch == ord('q'):
            break