#!/usr/bin/env python3
import time

import numpy as np

def convertir_a_nombre_archivo(segundosHoy):
    """
    Convertis the number of seconds from time.time() object to the file format compatible with the infringement detector
    """
    stringNombre = time.strftime("%Y%m%d_%H%M%S", time.localtime(segundosHoy))+'_'+("%0.2f" % segundosHoy).split('.')[-1]
    return stringNombre

def traffic_light_pixels(image, index):
    """
    Takes selected pixels from an image to process
    """
    pixels = np.array([image[index[0][1], index[0][0]]])
    for index in index[1:]:
        #pixels = np.append(pixels, np.array(imageArray[index[1], index[0]]))#, axis=0)
        pixels = np.append(pixels, [image[index[1], index[0]]], axis=0)

    #imagen = pixels.reshape(128, 2, 3)
    #new_imagen = cv2.resize(imagen, (24, 8), interpolation=cv2.INTER_CUBIC)
    return pixels