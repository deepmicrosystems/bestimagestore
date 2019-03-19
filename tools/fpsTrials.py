import os
import cv2
import time
import numpy as np

picam = False

numeroDeMuestras = 10

segundosHoy = time.time()
tiempoInicial = segundosHoy

nombre = time.strftime("%Y%m%d_%H%M%S_%f", time.localtime(segundosHoy))

if picam:
    import picamera
    from picameraArray import PiRGBAArray
    camera = picamera.PiCamera( resolution=(1920,1080))
    camera.exposure_mode = 'sports'
    camera.sensor_mode = 1

    lowResCap = PiRGBAArray(camera)

    lowResStream = camera.capture_continuous(lowResCap,
                                            format="bgra",
                                            use_video_port=True,
                                            splitter_port=2)
else:
    miCamara = cv2.VideoCapture(1)
    miCamara.set(3,1920)
    miCamara.set(4,1080)
    miCamara.set(cv2.CAP_PROP_FPS,30)

for i in range(numeroDeMuestras):
    tiempoInicial = time.time()
    if picam:
        lrs = lowResStream.__next__()
        lowRes_array = lrs.array
        lowResCap.truncate(0)
    else:
        _, lowRes_array = miCamara.read()
    print(time.time()-tiempoInicial)
    cv2.imwrite(os.getenv('HOME')+'/sample{}.jpg'.format(i), lowRes_array)
    #cv2.imshow('Visualization', lowRes_array)
#print(camera.sensor_mode)

