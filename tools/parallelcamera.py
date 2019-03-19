#!/usr/bin/env python

import os
import cv2
import sys
import numpy as np
import multiprocessing
from time import sleep, time

from ..pathsandnames import PathsAndNames
from .picamera_simulation import PiCameraSimulation

sys.path.append(os.getenv('HOME')+'/trafficFlow/surveillancecameratrafficlightcolor/')
from trafficlight import TrafficLight

class ParallelCamera(multiprocessing.Process):
    """
        5MP
        width: int:  2592       *2560
        height: int: 1944       *1920

        16 factor x(160,120)

        8MP
        width: int:  3280
        height: int: 2464
    """

    def __init__(self,
                 video_source = 0,
                 width = 2560,
                 height = 1920,
                 simulation = False,
                 pipe = None,
                 periodoSemaforo = 0,
                 show_trafficlight = False):

        super(ParallelCamera, self).__init__()

        self.simulation = simulation

        self.show_trafficlight = show_trafficlight

        # General parameters

        self.video_source = video_source
        self.width = width    # Integer Like
        self.height = height  # Integer Like

        # Variable para marcar paquete de señal de Stand-by
        self.last_order = 1

        # Set the input pipe for Stand-by signal
        self.out_pipe = pipe

        # Set Queue for send image outputs
        self.in_pipe = PathsAndNames.in_pipe
        # Instantiate Semaforo
        self.semaforo = TrafficLight(periodoSemaforo = periodoSemaforo,visualizacionDebug = False)
        PathsAndNames.miReporte.info('EXITOSAMENTE CREE LA CLASE ParallelCamera!!!')

    def stop(self):
        pass

    def run(self):
        """
            Main Loop / parallel process  for write images onto WorkDir/

            :input: standby: Bool (via pipe)
            :return: Void : Write in SD images if standby is False
            :modes: Simulation and Real Worldwork
        """
        # Load ROI Parameters in PiCamera format( 0 to 1) for P1 and P2

        if self.simulation:
            camera = PiCameraSimulation()
            PathsAndNames.miReporte.info('Started in emulated camera mode')
        else:
            import picamera
            from .picameraArray import PiRGBAArray
            camera = picamera.PiCamera( resolution=(self.width, self.height),
                                        framerate=2)
            PathsAndNames.miReporte.info('Started in real Pi camera mode')

        # Makes zoom to a region of interest between poinst P0 = (0,0) and P1 = (width,height)
        #camera.zoom = (0, 0, self.width, self.height)
        camera.exposure_mode = 'sports'
        # self.camera.shutter_speed      = 190000
        # self.camera.iso                = 800

        if not self.simulation:
            # We create a output object as a canvas to receive the images:
            lowResCap = PiRGBAArray(camera, size=(self.width,self.height))
            # Set low resolution stream as continuous
            lowResStream = camera.capture_continuous(lowResCap,
                                                     format="bgra",
                                                     use_video_port=True,
                                                     splitter_port=2,
                                                     resize=(self.width,self.height))
        # IMPORTANT!
        # resize above is redundant but black screen problem if removed.
        # This may cause a "Pata coja" effect
        # To be improved with v1 camera

        while True:
            """
            Maintain the constant saving  PiCamera  HD  and Semaforo LR frames to disk and
            send analysis from semaforo pixeles to main program via Queue.
            """
            # Keep track for standby input
            if self.out_pipe.poll():
                self.last_order = self.out_pipe.recv()
            
            if not self.simulation:
                lrs = lowResStream.__next__()
                high_resolution_image = lrs.array
                # Truncate low res frame
                lowResCap.truncate(0)
                # Obtain pixeles for LowRes frame
                pixeles = PathsAndNames.traffic_ligth_pixeles(high_resolution_image)
            else:
                pixeles = np.zeros((192,8), dtype=int)

            # Get traffic light and get the color as integer
            colourFound, flanco = self.semaforo.estadoSemaforo(pixeles)
            #semaforo_array = np.reshape(pixeles, (24, 8, 3))
            color_asinteger = colourFound%4

            actual_datestamp_array = 0

            # Check if standby or not
            if self.last_order > 0:
                # Obtain Actual Datetime stamp for this iteration of while loop
                actual_datestamp_array = time()
                nombreDeArchivo = PathsAndNames.convertirANombreArchivo(actual_datestamp_array)

                # Si el color es el apropiado se manda por pipe y se guarda en disco, caso contrario se manda por pipe el vector nulo para mantener el track del flanco y el color
                if (colourFound > 0) or (self.last_order == 1):
                    if self.simulation is False:
                        if self.show_trafficlight:
                            high_resolution_image = cv2.polylines(high_resolution_image, [PathsAndNames.traffic_light_poly], True, (255,255,255),4)       # Draw
                            #cv2.imwrite(PathsAndNames.directorioDeCaptura+'/'+nombreDeArchivo+'pixeles_{}.jpg'.format(color_asinteger), np.reshape(pixeles,(24,8,4)))
                        cv2.imwrite(PathsAndNames.directorioDeCaptura+'/'+nombreDeArchivo+'_{}.jpg'.format(color_asinteger),
                                    high_resolution_image[PathsAndNames.regionOfInterest[0][1]:PathsAndNames.regionOfInterest[1][1],PathsAndNames.regionOfInterest[0][0]:PathsAndNames.regionOfInterest[1][0]])
                    else:
                        camera.capture_sequence(dst_name=PathsAndNames.directorioDeCaptura+'/'+nombreDeArchivo+'_{}.jpg'.format(color_asinteger),resolution=(320,240))
            
            self.in_pipe.send((actual_datestamp_array, color_asinteger,flanco))