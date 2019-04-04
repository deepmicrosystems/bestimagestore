#!/usr/bin/env python3

import os
import cv2
import sys
import json
import logging
import numpy as np
from time import time
from datetime import datetime

from tools.background import Background
from tools.databasehandler import DataBaseHandler
from tools.methods import convertir_a_nombre_archivo
from tools.picamera_emulator import PiCameraEmulator

sys.path.append(os.getenv('TRAFFICLIGHT')+'/')
from trafficlight import TrafficLight

sys.path.append(os.getenv('HOME')+'/trafficFlow/preview/')
from highpicamera import HighPiCamera

class HighResolutionRecorder():
    """
    In this class we capture only the most relevant features in high resolution video from a pi camera at a maximum fps of 1 fps
    """

    def __init__(   self,
                    width = 2560,
                    height = 1920,
                    ratio = 8,
                    emulate = False,
                    save_low_resolution = 0,
                    show = False,
                    maximum_seconds_in_disk = 10):

        # Setting the parameters as object variables:
        self._width  = width
        self._height = height
        self._best_region = [(0,0),(self._width,self._height)]
        self.ratio = ratio
        self._emulate = emulate 
        self.apply_roi = False
        self.save_low_resolution = save_low_resolution
        self._current_time = time()
        self.my_periods = []
        self.maximum_seconds_in_disk = maximum_seconds_in_disk
        # We create the background substraction module:
        self.background = Background(scale=self.ratio, show = show, width = self._width, height = self._height)

        # Timing features:
        self._init_time = time()

        # Labels
        self.current_name = "Noname"

        # Canvas for the image:
        self.high_resolution_image = np.zeros((self._width,self._height,4))

        # We get the source and destiny folders:
        self.source = os.getenv('SOURCE_FOLDER_PATH')
        self.todayFolder = os.getenv('TODAY_FOLDER')
        self.movement_path = os.getenv('MOVEMENT_PATH')

        if not os.path.exists(self.todayFolder):
            os.system('mkdir ' + self.todayFolder)
            os.system('mkdir ' + self.movement_path)

        # We create the database:
        self.my_database = DataBaseHandler(os.getenv('TODAY_FOLDER')+'/movement_sensor.db')
        logging.debug('Database created successfully')

        # We verify the destiny folder is empty:
        os.system('sudo rm -rf ' + self.movement_path)
        os.system('mkdir ' + self.movement_path)

        self.test_camera = HighPiCamera(width = self._width,
                                        height = self._height,
                                        framerate = 2,
                                        emulate = self._emulate)
        # IMPORTANT!
        # Resize above is redundant but black screen problem if removed.
        # This may cause a "Pata coja" effect
        # To be improved with v1 camera

        self._trafficlight_pixels = np.zeros((192,8), dtype=int)

    def priorize_region(self,best_region):
        self._best_region = best_region

    def obtain_coincidence(self,rectangle1):
        # The next three lines calculate the overlap area between the two rectangles:
        best_x_min, best_y_min = self._best_region[0]
        best_x_max, best_y_max = self._best_region[1]
        x_overlap = max(0, min(rectangle1[1][0], self._best_region[1][0]) - max(rectangle1[0][0], self._best_region[0][0]))
        y_overlap = max(0, min(rectangle1[1][1], self._best_region[1][1]) - max(rectangle1[0][1], self._best_region[0][1]))
        overlapArea = x_overlap * y_overlap
        reference_area = (best_x_max - best_x_min) * (best_y_max - best_y_min)
        coincidence = int(overlapArea/reference_area*100)
        logging.debug('Overlap area: {}/ Reference: {} = {}'.format(overlapArea,reference_area,coincidence))
        return coincidence

    def my_fps(self):
        return 1/self.my_period()

    def my_period(self):
        return sum(self.my_periods)/len(self.my_periods)

    def get_low_resolution_image(self):
        return self.background.get_low_resolution_image()

    def get_image(self):
        """
        We acquire and process a new image:
        """
        # We set the new time, calculate the period and take care we don't overflow the memory
        # by checking the lenght of the list is never greater than 15
        new_current_time = time()
        self.my_periods.append(new_current_time - self._current_time)

        if len(self.my_periods) > 15:
            self.my_periods.pop(0)
        
        # We start with the main process
        self._current_time = new_current_time

        ret, self.high_resolution_image = self.test_camera.read()

        self.current_name = convertir_a_nombre_archivo(self._current_time)
        logging.debug(self._current_time)
        logging.debug(self.current_name)
        return self.high_resolution_image

    def save_images(self, state, exclude_range = 50):
        base_name = self.movement_path + '/' + self.current_name + '_s{}'.format(state)
        # If we must report some soconds of Foreground in high resolution:
        if self.maximum_seconds_in_disk:
            rectangles = self.background.get_foreground(self.high_resolution_image)
            logging.debug('Saving {} rectangles'.format(len(rectangles)))
            for index,rectangle in enumerate(rectangles):
                (x,y,w,h) = rectangle
                coincidence = self.obtain_coincidence([(x,y),(x+w,y+h)])
                logging.debug('COINCIDENCE: {}'.format(coincidence))
                if coincidence > exclude_range:
                    high_resolution_name = base_name + '_c{}_{}_high.jpg'.format(coincidence,index)
                    cv2.imwrite(high_resolution_name, self.high_resolution_image[y:y+h,x:x+w])
                    # We report to the database:
                    self.my_database.insert_new_element(self._current_time,state,index,x,y,w,h)

            # We verify the maximum time in the past that we store:
            self.my_database.purge_images_before(time() - self.maximum_seconds_in_disk)

        # If we must store the first seconds in high resolution:
        if time() - self._init_time < self.save_low_resolution:
            low_resolution_name = base_name + '_low.jpg'
            cv2.imwrite(low_resolution_name, self.get_low_resolution_image())

    # Setters and getters:
    def set_emulate(self,new_emulate_state):
        self._emulate = new_emulate_state

    def __del__(self):
        self.my_database.close_database()


