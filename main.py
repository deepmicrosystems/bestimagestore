#!/usr/bin/env python3

import os
import cv2
import logging
import argparse
import datetime

from highresolutionrecorder import HighResolutionRecorder

parser = argparse.ArgumentParser(description = 'Settings configurations for the shutter class')
parser.add_argument('-W', '--width',     type = int,  default = '2560', help = 'Widht of the picture')
parser.add_argument('-H', '--heigth',    type = int,  default = '1920', help = 'Heigth of the picture in pixels')
parser.add_argument('-r', '--roi',       type = bool, default = False,  help = 'Enable ROI')
parser.add_argument('-s', '--show',      type = bool, default = False,  help = 'Show frames in real time')
parser.add_argument('-i', '--input',     type = str,  default = None,   help = 'File or folder to display in emulated mode')
parser.add_argument('-d', '--debug',     type = bool, default = False,  help = 'Starts in debug mode')
#parser.add_argument('-s', '--save',   type = bool, default = False,  help = 'Save all low resolution frames')
args = parser.parse_args()

my_level = logging.INFO
if args.debug:
    my_level = logging.DEBUG

# We set the logging module:
logging.basicConfig(filename='bestimagestore.txt', filemode='w', format='%(name)s - %(asctime)s : %(message)s',level=my_level)

# To display de fps we make use of:
counter = 0
period_to_display = 10

if __name__ == "__main__":
    # By default we do not use simulation mode unless otherwise stated:
    simulation = False

    # If an input was introduced we use the simulation mode:
    if args.input:
        simulation = True

    #If we are not in a Lucam camera we also use the simulation mode:
    if (os.uname()[1][:5].lower() != 'lucam'):
        simulation = True 

    myRecorder = HighResolutionRecorder(width = 2560,
                                        height = 1920,
                                        simulation = simulation,          # False
                                        apply_roi = False,
                                        apply_background = False,
                                        save_low_resolution = False,
                                        trafficlight = None)

    while True:
        image = myRecorder.process_new_image()
        ch = cv2.waitKey(1)
        message = 'FPS: {0:.2f} and period: {1:.2f}'.format(myRecorder.my_fps(),myRecorder.my_period())
        if counter%period_to_display == 0:
            logging.info(message)
        else:
            logging.debug(message)
        if args.show:
            cv2.imshow('Display', image)
        if ch == ord('q'):
            break
        counter += 1