import numpy as np
import cv2
import imutils

class Layer:
    #bounds = [[(x,y,w,h), ],]

    startFrame = None
    lastFrame = None
    length = None

    def __init__(self, startFrame, data, mask, config):
        '''returns a Layer object
        
        Layers are collections of contours with a StartFrame, 
        which is the number of the frame the first contour of
        this layer was extraced from

        A Contour is a CV2 Contour, which is a y*x*3 rgb numpy array,
        but we only care about the corners of the contours. 
        So we save the bounds (x,y,w,h) in bounds[] and the actual content in data[] 
        '''
        self.startFrame = startFrame
        self.lastFrame = startFrame
        self.config = config
        self.data = []
        self.bounds = []
        self.masks = []
        self.stats = dict()

        self.bounds.append([data])
        self.masks.append([mask])
        #print("Layer constructed")

    def add(self, frameNumber, bound, mask):
        '''Adds a bound to the Layer at the layer index which corresponds to the given framenumber'''
        index = frameNumber - self.startFrame

        if frameNumber > self.lastFrame:
            for i in range(frameNumber - self.lastFrame):
                self.bounds.append([bound])
                self.masks.append([mask])

            self.lastFrame = frameNumber

        if bound not in self.bounds[index]:
            self.bounds[index].append(bound)
            self.masks[index].append(mask)


    def calcStats(self):
        '''calculates average distance, variation and deviation of layer movement'''
        middles = []
        for i, bounds in enumerate(self.bounds):
            for j, bound in enumerate(bounds):
                if None in bound:
                    continue
                x = (bound[0] + bound[2]/2) 
                y = (bound[1] + bound[3]/2) 
                middles.append([x,y])
        
        avg = 0 
        for i in range(1, len(middles), 2):
            avg += (((float(middles[i][0]-middles[i-1][0])/len(middles))**2 + float(middles[i][1]-middles[i-1][1])/len(middles))**2)**(1/2)
        self.stats = dict()
        self.stats["avg"] = round(avg,2) 

        x=0
        for i in range(1, len(middles), 2):
            x += (((((float(middles[i][0]-middles[i-1][0])/len(middles))**2 + float(middles[i][1]-middles[i-1][1])/len(middles))**2)**(1/2)) - avg)**2

        x /= (len(middles)-1) 

        self.stats["var"] = round(x,2)
        self.stats["dev"] = round((x)**(1/2), 2)
        

    def getLength(self):
        return len(self)

    def __len__(self):
        self.length = len(self.bounds)
        return self.length
   
