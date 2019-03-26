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

from tools.methods import convertir_a_nombre_archivo
from tools.picamera_emulator import PiCameraEmulator

sys.path.append(os.getenv('TRAFFICLIGHT')+'/')
from trafficlight import TrafficLight

class HighResolutionRecorder():
    """
    In this class we capture only the most relevant features in high resolution video from a pi camera at a maximum fps of 1 fps
    """

    def __init__(   self,
                    width = 2560,
                    height = 1920,
                    ratio = 8,
                    simulation = False,
                    apply_background = False,
                    save_low_resolution = 0,
                    show = False):

        # Setting the parameters as object variables:
        self._width  = width
        self._height = height
        self.ratio = ratio
        self._simulation = simulation 
        self.apply_roi = False
        self.apply_background = apply_background
        self.save_low_resolution = save_low_resolution
        self._current_time = time()
        self.my_periods = []
        # We create the background substraction module:
        self.background = Background(scale=self.ratio, show = show, width = self._width, height = self._height)

        # Timing features:
        self._init_time = time()

        # Labels
        self.current_name = "Noname"

        # Canvas for the image:
        self.high_resolution_image = np.zeros((self._width,self._height,4))
        self.low_resolution_image = np.zeros((int(self._width//self.ratio),int(self._height//self.ratio),3))

        # We get the source and destiny folders:
        self.source = os.getenv('SOURCE_FOLDER_PATH')
        self.todayFolder = os.getenv('DESTINY_HIGH_RESOLUTION_PATH') + '/' + datetime.now().strftime('%Y%m%d')
        self.destiny =  self.todayFolder + '/movementSensor'

        if not os.path.exists(self.todayFolder):
            os.system('mkdir ' + self.todayFolder)
            os.system('mkdir ' + self.destiny)

        # We verify the destiny folder is empty:
        os.system('sudo rm -rf ' + self.destiny)
        os.system('mkdir ' + self.destiny)

        # We create the camera interface in simulation and normal mode
        if self._simulation:
            self.camera = PiCameraEmulator(self.source)
            logging.info('Started in Simulation mode')
        else:
            import picamera 
            from tools.picameraArray import PiRGBAArray
            self.camera = picamera.PiCamera(resolution = (self._width,self._height),
                                            framerate  = 2)
            logging.info('Started in PiCamera Mode')
        self.camera.exposure_mode = 'sports'

        # We create the canvas to receive the image object:
        if self._simulation:
            self.frame_stream = self.camera
        else:
            self._frame_output = PiRGBAArray(   self.camera,
                                                size = (self._width,self._height))

            self.frame_stream = self.camera.capture_continuous( self._frame_output,
                                                                format="bgra",
                                                                use_video_port=True,
                                                                splitter_port=2,
                                                                resize=(self._width,self._height))

        # IMPORTANT!
        # Resize above is redundant but black screen problem if removed.
        # This may cause a "Pata coja" effect
        # To be improved with v1 camera

        self._trafficlight_pixels = np.zeros((192,8), dtype=int)

    def my_fps(self):
        return 1/self.my_period()

    def my_period(self):
        return sum(self.my_periods)/len(self.my_periods)

    def get_low_resolution_image(self):
        self.low_resolution_image = cv2.resize(self.high_resolution_image,(self.high_resolution_image.shape[1]//self.ratio,self.high_resolution_image.shape[0]//self.ratio))
        return self.low_resolution_image

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

        if not self._simulation:
            image_object = self.frame_stream.__next__()
            self.high_resolution_image = image_object.array
            # Truncate low res frame
            self._frame_output.truncate(0)
        else:
            self.high_resolution_image = self.frame_stream.__next__()

        self.current_name = convertir_a_nombre_archivo(self._current_time)
        return self.high_resolution_image

    def save_images(self, state):
        base_name = self.destiny + '/' + self.current_name + '_s{}'.format(state)

        # Background
        if self.apply_background:
            rectangles = self.background.get_foreground(self.high_resolution_image)
            print('Saving {} rectangles'.format(len(rectangles)))
            for index,rectangle in enumerate(rectangles):
                (x,y,w,h) = rectangle
                high_resolution_name = base_name + '_{}_high.jpg'.format(index)
                cv2.imwrite(high_resolution_name, self.high_resolution_image[y:y+h,x:x+w])

        if time() - self._init_time < self.save_low_resolution:
            low_resolution_name = base_name + '_low.jpg'
            cv2.imwrite(low_resolution_name, self.get_low_resolution_image())

    # Setters and getters:
    def set_simulation(self,new_simulation_state):
        self._simulation = new_simulation_state


