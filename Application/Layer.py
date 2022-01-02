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
        self.exportOffset = 0

        self.bounds.append([data])
        self.masks.append([mask])
        #print("Layer constructed")

    def add(self, frameNumber, bound, mask):
        '''Adds a bound to the Layer at the layer index which corresponds to the given framenumber'''
        index = frameNumber - self.startFrame
        if index < 0:
            return
        if frameNumber > self.lastFrame:
            for i in range(frameNumber - self.lastFrame):
                self.bounds.append([])
                self.masks.append([])
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

    def spaceOverlaps(self, layer2):
        '''Checks if there is an overlap in the bounds of current layer with given layer'''
        overlap = False
        maxLen = min(len(layer2.bounds), len(self.bounds))
        bounds = self.bounds[:maxLen]
        for b1s, b2s in zip(bounds[::10], layer2.bounds[:maxLen:10]):
            for b1 in b1s:
                for b2 in b2s:
                    if self.contoursOverlay((b1[0], b1[1]+b1[3]), (b1[0]+b1[2], b1[1]), (b2[0], b2[1]+b2[3]), (b2[0]+b2[2], b2[1])):
                        overlap = True
                        break
        return overlap
    
    def timeOverlaps(self, layer2):
        '''Checks for overlap in time between current and given layer'''
        s1 = self.exportOffset
        e1 = self.lastFrame - self.startFrame + self.exportOffset
        s2 = self.exportOffset
        e2 = layer2.lastFrame - layer2.startFrame + self.exportOffset

        if s2 >= s1 and s2 <= e1:
            return True
        elif s1 >= s2 and s1 <= e2:
            return True
        else:
            return False

    def contoursOverlay(self, l1, r1, l2, r2):
        if(l1[0] >= r2[0] or l2[0] >= r1[0]):
            return False
        if(l1[1] <= r2[1] or l2[1] <= r1[1]):
            return False
        return True
   
