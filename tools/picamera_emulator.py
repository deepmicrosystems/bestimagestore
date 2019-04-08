#!/usr/bin/env python3

import os
import cv2
import time

class PiCameraEmulator():
    """
    General PICAMERA Emulator in for trials in a computer other that the raspberry pi
    """

    path_to_image_folder = os.getenv('SOURCE_FOLDER_PATH')

    def __init__(self, path_to_high_resolution_images = 'None'):
        # Private attributes:
        self._number_of_images = 0
        self._counter = 0

        # Public attributes:
        self.zoom = (0,0,0,0)
        self.exposure_mode = ""

        if path_to_high_resolution_images:
            self.change_pictures_folder(path_to_high_resolution_images)
        else:
            self.change_pictures_folder(PiCameraEmulator.path_to_image_folder)

    def change_pictures_folder(self, new_folder):
        self._list_of_images = sorted([image for image in os.listdir(new_folder) if '.jpg' in image or '.png' in image])
        self._number_of_images = len(self._list_of_images)
        self._counter = 0
        #print('Loaded: {} with {} images'.format(new_folder,self._number_of_images))

    def __next__(self):
        path_to_image = PiCameraEmulator.path_to_image_folder + '/' + self._list_of_images[self._counter%self._number_of_images]
        self._counter += 1
        image = cv2.imread(path_to_image)
        return image