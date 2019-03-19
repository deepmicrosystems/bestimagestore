#!/usr/bin/env python
# shutter_intercafe.py

"""
This script serve as interface for methods inside of .shutter package
"""
import os
import multiprocessing
from ownLibraries.pathsandnames import PathsAndNames
from .shutterFiles.parallelcamera import ParallelCamera
#from .shutter import picontrolador


class MultiprocessCameraController():
    """
    States:
    0 -> Off
    1 -> On and savig everything
    2 -> On and saving red light only
    3 -> On and saving re light and movement only
    """
    def __init__(self,
                 video_source = 0,
                 width = 2560,                  #2592,
                 height = 1920,                 #1944,
                 simulation = False,
                 periodoSemaforo = 0,
                 show_trafficlight = False):

        self.estado = 1

        self.simulation = simulation
        if not simulation:
            # If this is not forced it decides according to the device, Pi or PC
            # The standard hostname for enforcement cameras is LUCAM or lucam
            if (os.uname()[1][:5] != 'LUCAM') and (os.uname()[1][:5] != 'lucam'):
                self.simulation = True
                print('Not on Lucam, emulating tureturer')

        # Initial parameters
        self.out_pipe_pass_to_camera, self.in_pipe_control_camera = multiprocessing.Pipe(duplex=False)

        self.video_source 		= video_source
        self.width 				= width		# Integer Like
        self.height 			= height	# Integer Like

        self.shutter = ParallelCamera(  video_source = self.video_source,
                                        width = self.width,
                                        height = self.height,
                                        simulation = self.simulation,
                                        pipe = self.out_pipe_pass_to_camera,
                                        periodoSemaforo = periodoSemaforo,
                                        show_trafficlight = show_trafficlight)
        self.shutter.start()
        PathsAndNames.miReporte.info('EXITOSAMENTE CREE LA CLASE SHOOTERv11!!!')

    def pause_shutter(self):
        PathsAndNames.miReporte.info('Pausing Camera')
        self.estado = 0
        self.stand_by(self.estado)

    def capture_all_frames(self):
        PathsAndNames.miReporte.info('Capturing all frames')
        self.estado = 1
        self.stand_by(self.estado)

    def capture_only_red_light_crosses(self):
        PathsAndNames.miReporte.info('Capturing red light crosses')
        self.estado = 2
        self.stand_by(self.estado)
    
    def capture_saving_mode(self):
        PathsAndNames.miReporte.info('Capturing red light movement crosses')
        self.estado = 3
        self.stand_by(self.estado)

    def stop(self):
        PathsAndNames.miReporte.warning('Stopped Capturer')
        self.estado = 0
        self.shutter.stop()
        self.shutter.terminate()

    def stand_by(self, estado):
        self.in_pipe_control_camera.send(estado)
