#!/usr/bin/env python3
import os
import time
import socket
import datetime
import numpy as np

def convertir_a_nombre_archivo(segundosHoy):
    """
    Convertis the number of seconds from time.time() object to the file format compatible with the infringement detector
    """
    stringNombre = time.strftime("%Y%m%d_%H%M%S", time.localtime(segundosHoy))+'_'+("%0.2f" % segundosHoy).split('.')[-1]
    return stringNombre

def convertir_de_nombre_a_segundos(string_name,timezone = -4):
    """
    The String name must be in the form YYYYmmdd_HHMMSS_ff
    ff are the centiseconds
    """
    #print('Before: ',string_name)
    #print("Here: ",int(string_name[9:11]),timezone)
    
    string_to_time = datetime.datetime(int(string_name[0:4]),       # YYYY
                                    int(string_name[4:6]),          # mm
                                    int(string_name[6:8]),          # dd
                                    int(string_name[9:11]),         # HH
                                    int(string_name[11:13]),        # MM
                                    int(string_name[13:15]),        # SS
                                    int(string_name[16:18])*10000)  # ff0000
    string_to_time = string_to_time - datetime.timedelta(hours=timezone)

    epoch = datetime.datetime.utcfromtimestamp(0)
    seconds = (string_to_time-epoch).total_seconds()
    if not convertir_a_nombre_archivo(seconds) == string_name:
        #print("Alerta de conversión str: ",convertir_a_nombre_archivo(seconds),string_name)
        return None 
    else:
        #print("Equals: ",convertir_a_nombre_archivo(seconds),string_name)
        return seconds

def convert_to_db_datetime(seconds_since_epoch):
    # Converts seconds since epoch to standar ISO 8601: YYYY-MM-DD HH:MM:SS.mmmmmm'
    str_seconds = '{0:.2f}'.format(seconds_since_epoch)
    time_iso_format = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(seconds_since_epoch)) + '.' + str_seconds[-2:]
    return time_iso_format

def convertir_de_iso8601_a_segundos(string_name,timezone = -4):
    """
    The String name must be in the form YYYY-mm-dd HH:MM:SS.ff
    ff are the centiseconds
    """
    print('Before: ',string_name)
    print("Here: ",int(string_name[9:11]),timezone)
    
    string_to_time = datetime.datetime(int(string_name[0:4]),       # YYYY
                                    int(string_name[5:7]),          # mm
                                    int(string_name[8:10]),         # dd
                                    int(string_name[11:13]),        # HH
                                    int(string_name[14:16]),        # MM
                                    int(string_name[17:19]),        # SS
                                    int(string_name[20:22])*10000)  # ff0000
    string_to_time = string_to_time - datetime.timedelta(hours=timezone)

    epoch = datetime.datetime.utcfromtimestamp(0)
    seconds = (string_to_time-epoch).total_seconds()
    if not convert_to_db_datetime(seconds) == string_name:
        print("Alerta de conversión str: ",convertir_a_nombre_archivo(seconds),string_name)
        return None 
    else:
        print("Equals: ",convertir_a_nombre_archivo(seconds),string_name)
        return seconds

def convert_from_db_datetime(date_time_in_iso):
    # Converts standar ISO 8601: YYYY-MM-DD HH:MM:SS.mmmmmm time to seconds since epoch
    str_seconds = '{0:.2f}'.format(seconds_since_epoch)
    time_iso_format = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(seconds_since_epoch)) + '.' + str_seconds[-2:]
    return time_iso_format


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

def is_connected_to_internet():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

