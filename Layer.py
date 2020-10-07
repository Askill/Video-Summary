import numpy as np
import cv2
import imutils
class Layer:
    #data = [(contour, (x,y,w,h)),]

    startFrame = None
    lastFrame = None
    length = None

    def __init__(self, startFrame, data):
        self.startFrame = startFrame
        self.lastFrame = startFrame
        
        self.data = []
        self.bounds = []
        self.bounds.append(data)
        #print("Layer constructed")

    def add(self, frameNumber, data):
        if not (self.startFrame + len(self.bounds) - frameNumber < 0):
            self.lastFrame = frameNumber
         
            self.bounds.append(data)
        self.getLength()

    def getLength(self):
        self.length = len(self.bounds)
        return self.length
    
    def fill(self, inputPath, resizeWidth):
        '''reads in the contour data, needed for export'''
        
        cap = cv2.VideoCapture(inputPath) 
        self.data = [None]*len(self.bounds)
        i = 0
        cap.set(1, self.startFrame)
        while i < len(self.bounds):
            ret, frame = cap.read() 
            
            if ret:
                frame = imutils.resize(frame, width=resizeWidth)
                (x, y, w, h) = self.bounds[i]
                self.data[i] = frame[y:y+h, x:x+w]
            i+=1
        cap.release()
   


