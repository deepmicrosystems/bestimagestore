#!/usr/bin/env python3

import os
import sys
import cv2
import json
import logging
import argparse
import datetime
import numpy as np

from tools.methods import traffic_light_pixels
from highresolutionrecorder import HighResolutionRecorder

sys.path.append(os.getenv('TRAFFICLIGHT'))
from trafficlight import TrafficLight

parser = argparse.ArgumentParser(description = 'Settings configurations for the shutter class')
parser.add_argument('-W', '--width',        type = int,  default = '2560', help = 'Widht of the picture')
parser.add_argument('-H', '--heigth',       type = int,  default = '1920', help = 'Heigth of the picture in pixels')
#parser.add_argument('-r', '--roi',          type = bool, default = False,  help = 'Enable ROI')
parser.add_argument('-s', '--show',         type = bool, default = False,  help = 'Show frames in real time')
parser.add_argument('-e', '--emulate',      type = str,  default = None,   help = 'File or folder to display in emulated mode')
parser.add_argument('-d', '--debug',        type = bool, default = False,  help = 'Starts in debug mode')
parser.add_argument('-p', '--trafficlight', type = int,  default = None,   help = 'Export Traffic Light Information with the given period, if not stated the trafficlight unit wont init')
parser.add_argument('-l', '--low_saving',   type = int,  default = 0,      help = 'Period of seconds for saving low resolution images')
parser.add_argument('-c', '--coincidence',  type = int,  default = 20,      help = 'Required coincidence to store moving objects')
parser.add_argument('-b', '--back',         type = bool, default = False,  help = 'Enable Background saving')
#parser.add_argument('-s', '--save',   type = bool, default = False,  help = 'Save all low resolution frames')
args = parser.parse_args()

if __name__ == "__main__":
    # We set the logging module:
    my_level = logging.INFO
    if args.debug:
        my_level = logging.DEBUG
    logging.basicConfig(filename='bestimagestore.txt', filemode='w', format='%(name)s - %(asctime)s : %(message)s',level=my_level)

    # To display de fps we make use of:
    counter = 0
    period_to_logging = 10
    color_asinteger = 0

    # If an input was introduced we use the emulate mode:
    emulate = args.emulate

    myRecorder = HighResolutionRecorder(width = 2560,
                                        height = 1920,
                                        emulate = emulate,          # False
                                        apply_background = args.back,
                                        save_low_resolution = args.low_saving,
                                        show = args.show)

    # Setup the trafficlight:

    installFile = 'datos.json'

    with open(os.getenv('INSTALL_PATH')+'/'+installFile) as jsonData:
        install_data = json.loads(jsonData.read())

    best_region = install_data['highResolution']['mostLikelyRegion']
    myRecorder.priorize_region(best_region)

    if not args.trafficlight == None:
        trafficlight = TrafficLight(periodoSemaforo = args.trafficlight,visualizacionDebug = args.show, export_value = True)

    # LOOP
    while True:
        full_size_image = myRecorder.get_image()

        # Traffic light:
        # Notese esta corrección de división por dos:
        pixels = np.array(install_data['highResolution']['trafficLightPixels'])//2

        if not args.trafficlight == None:
            pixeles = traffic_light_pixels(full_size_image, pixels)
            colourFound, flanco = trafficlight.estadoSemaforo(pixeles)
            color_asinteger = colourFound%4
            logging.info('Colour found to be {}'.format(color_asinteger))

        myRecorder.save_images(state = color_asinteger, exclude_range=args.coincidence)
        
        message = 'FPS: {0:.2f} and period: {1:.2f}'.format(myRecorder.my_fps(),myRecorder.my_period())
        if counter%period_to_logging == 0:
            logging.info(message)
        else:
            logging.debug(message)

        # Display options
        if args.show:
            cv2.imshow('Display', myRecorder.get_low_resolution_image())

        # Display control
        ch = cv2.waitKey(1)
        if ch == ord('q'):
            break
        counter += 1