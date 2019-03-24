#!/usr/bin/env python3

import os
import cv2
import sys
import json
import logging
import numpy as np
from time import time

from tools.methods import traffic_light_pixels
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
                    simulation = False,
                    apply_roi = False,
                    apply_background = False,
                    save_low_resolution = False,
                    trafficlight = None,
                    place = None):

        # Setting the parameters as object variables:
        self._width  = width
        self._height = height
        self._simulation = simulation 
        self.apply_roi = False,
        self.apply_background = False,
        self.save_low_resolution = False,
        self._trafficlight_period = trafficlight
        self._current_time = time()
        self.my_periods = []

        # We get the source and destiny folders:
        self.source = os.getenv('SOURCE_FOLDER_PATH')
        self.destiny = os.getenv('DESTINY_HIGH_RESOLUTION_PATH')

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

        if not self._trafficlight_period == None:
            self.semaforo = TrafficLight(periodoSemaforo = self._trafficlight_period,visualizacionDebug = False)
        
        # IMPORTANT!
        # Resize above is redundant but black screen problem if removed.
        # This may cause a "Pata coja" effect
        # To be improved with v1 camera

        self._trafficlight_pixels = np.zeros((192,8), dtype=int)

        if place:
            self.installFile = place + '.json'
        else:
            self.installFile = 'datos.json'

        with open(os.getenv('INSTALL_PATH')+'/'+self.installFile) as jsonData:
            self.install_data = json.loads(jsonData.read())

    def my_fps(self):
        return 1/self.my_period()

    def my_period(self):
        return sum(self.my_periods)/len(self.my_periods)

    def process_new_image(self):
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
            high_resolution_image = image_object.array
            # Truncate low res frame
            self._frame_output.truncate(0)
        else:
            high_resolution_image = self.frame_stream.__next__()
        
        color_asinteger = 4
        # If required we get the pixels for the traffic light processing
        if not self._trafficlight_period == None:
            pixeles = traffic_light_pixels(high_resolution_image, install_data['highResolution']['trafficLightPixels'])
            colourFound, flanco = self.semaforo.estadoSemaforo(pixeles)
            #semaforo_array = np.reshape(pixeles, (24, 8, 3))
            color_asinteger = colourFound%4

        nombreDeArchivo = convertir_a_nombre_archivo(self._current_time)

        cv2.imwrite(self.destiny + '/' + nombreDeArchivo + '_{}.jpg'.format(color_asinteger),
                    high_resolution_image)

        if self._trafficlight_period is not None:
            self.export_trafficlight_color(colourFound)

        return high_resolution_image
        
            
    def export_trafficlight_color(self, current_color):
        pass

    # Setters and getters:
    def set_simulation(self,new_simulation_state):
        self._simulation = new_simulation_state


