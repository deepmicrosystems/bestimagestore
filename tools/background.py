import cv2
import numpy as np

class Background():
    def __init__(self,scale = 1,show = False, width = 2560, height = 1920):
        self.fgbgNew = cv2.createBackgroundSubtractorMOG2()
        self.show = show
        self.scaleFactor = scale
        self.w_min = int(0.7*width//self.scaleFactor//2)
        self.h_min = int(0.7*height//self.scaleFactor//2)
        self.h_max = int(1.4*width//self.scaleFactor//2)
        self.w_max = int(1.4*height//self.scaleFactor//2)

        self.optimal_step = 1

        self.imagenActual = np.zeros((width//self.scaleFactor,height//self.scaleFactor,3))

    def get_foreground(self,imagenActual):
        #self.imagenActual = cv2.cvtColor(imagenActual,cv2.COLOR_BGR2GRAY)
        self.imagenActual = cv2.resize(imagenActual,(imagenActual.shape[1]//self.scaleFactor,imagenActual.shape[0]//self.scaleFactor))
        
        self.imagenActual = cv2.GaussianBlur(self.imagenActual,(17,17),0)
        #self.imagenActualBS = cv2.medianBlur(self.imagenActualBS,11,0)
        #self.imagenActualBS = cv2.morphologyEx(self.imagenActualBS, cv2.MORPH_OPEN, self.kernel)
        fgmask = self.fgbgNew.apply(self.imagenActual)
        
        #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)
        if self.show:
            cv2.imshow('Mask', fgmask)

        _, contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  #,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        rectangles = []
        for (index, contour) in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            
            # We add to our list the appropriate sizes only
            if ((h > self.h_min) or (w > self.w_min)) and ((h < self.h_max) or (w < self.w_max)):
                rectangles.append((self.scaleFactor*x, self.scaleFactor*y, self.scaleFactor*w, self.scaleFactor*h))
                if self.show:
                    drawn_image = cv2.rectangle(self.imagenActual, (x,y), (x+w,y+h), (255,255,255), 2, -1)
                    cv2.imshow('Background', drawn_image)

                

        return rectangles

    def get_foreground_contrib(self,imagenActualEnGris,area):
        self.imagenActualBS = area.enmarcar(imagenActualEnGris)
        #self.imagenActualBS = cv2.GaussianBlur(self.imagenActualBS,(11,11),0)
        #cv2.imshow('Blur',self.imagenActualBS)
        #fgmask = self.fgbg.apply(self.imagenActualBS)
        #self.imagenActualBS = cv2.GaussianBlur(self.imagenActualBS,(7,7),0)
        fgmask = self.fgbgNew.apply(self.imagenActualBS)
        #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)

        _, contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

        #fgmask = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
        rectangulos = [cv2.boundingRect(contour) for contour in contours]
        rectangulosOriginales = []
        for rec in rectangulos:
            (x,y,w,h) = rec
            if (h>32/self.optimal_step)&(w>24/self.optimal_step):		# Afectado por el resize en perspective
                rectangulosOriginales.append((x*self.optimal_step+area.xmin,y*self.optimal_step+area.ymin,w*self.optimal_step,h*self.optimal_step))
        for (index, contour) in enumerate(contours):
            contour = cv2.convexHull(contour)
            #double epsilon = 3;

            #cv2.approxPolyDP(hull, approx, epsilon, true);
            #cv2.drawContours(fgmask, contour, -1, (255-25*index,25*index,0), 3)

            (x, y, w, h) = cv2.boundingRect(contour)
            if (h>36)&(w>24):
                cv2.rectangle(fgmask, (x, y), (x+w, y+h), (255,0,0), 1)

        #self.imagenAuxiliarBS = self.imagenActualBS
        #sys.stdout.write("\033[F") # Cursor up one line

        #cv2.imshow('Partida',self.areaDePartidaDesdeArriba.transformar(self.imagenAuxiliar,height = 60))
        #cv2.imshow('Media',self.areaMediaDesdeArriba.transformar(self.imagenAuxiliar,height = 60))
        #cv2.imshow('Main',fgmask)
        return rectangulosOriginales
