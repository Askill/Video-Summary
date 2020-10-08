from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import os
import traceback
import _thread
import imageio
import numpy as np
import time
from threading import Thread
from multiprocessing import Queue, Process, Pool
from multiprocessing.pool import ThreadPool
import concurrent.futures

class ContourExtractor:

    #X = {frame_number: [(contour, (x,y,w,h)), ...], }
    extractedContours = dict()
    min_area = 500
    max_area = 28000
    threashold = 13
    xDim = 0
    yDim = 0

    def getextractedContours(self):
        return self.extractedContours

    def __init__(self):
        print("ContourExtractor initiated")

    def extractContours(self, videoPath, resizeWidth):


        # initialize the first frame in the video stream
        vs = cv2.VideoCapture(videoPath)

        res, image = vs.read()
        self.xDim = image.shape[1]
        self.yDim = image.shape[0]
        firstFrame = None
        # loop over the frames of the video
        frameCount = -1
        extractedContours = dict()
        
        results = []
        extractedContours = dict()

        imageBuffer = []
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            while res:
                frameCount += 1
                if frameCount % (60*30) == 0:
                    print("Minutes processed: ", frameCount/(60*30))
                

                res, frame = vs.read()
                # resize the frame, convert it to grayscale, and blur it
                if frame is None:
                    print("ContourExtractor: frame was None")
                    break

                frame = imutils.resize(frame, width=resizeWidth)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

                # if the first frame is None, initialize it
                if firstFrame is None:
                    gray = np.asarray(gray[:,:,1]/2 + gray[:,:,2]/2).astype(np.uint8)       
                    gray = cv2.GaussianBlur(gray, (5, 5), 0)
                    firstFrame = gray
                    continue

                results.append(executor.submit(self.getContours, frameCount, gray, firstFrame))

                #contours = self.getContours(frameCount, gray, firstFrame)

            for f in concurrent.futures.as_completed(results):
                x=f.result()
                if x is not None:
                    extractedContours = {**extractedContours, **x} 
        
        self.extractedContours = extractedContours
        return extractedContours
            
    def getContours(self, frameCount, gray, firstFrame):
        gray = np.asarray(gray[:,:,1]/2 + gray[:,:,2]/2).astype(np.uint8)       
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        frameDelta = cv2.absdiff(gray, firstFrame)
        thresh = cv2.threshold(frameDelta, self.threashold, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        thresh = cv2.dilate(thresh, None, iterations=3)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        contours = []
        for c in cnts:
            ca = cv2.contourArea(c)
            if ca < self.min_area or ca > self.max_area:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            #print((x, y, w, h))
            contours.append((x, y, w, h))

        if len(contours) != 0: 
            return {frameCount: contours}
        else:
            return None

    def displayContours(self):
        values = self.extractedContours.values()
        for xx in values:
            for v1 in xx:
                (x, y, w, h) = v1[1]
                v = v1[0]
                frame = np.zeros(shape=[self.yDim, self.xDim, 3], dtype=np.uint8)
                frame = imutils.resize(frame, width=512)
                frame[y:y+v.shape[0], x:x+v.shape[1]] = v
                cv2.imshow("changes overlayed", frame)
                cv2.waitKey(10) & 0XFF
        cv2.destroyAllWindows()

    def exportContours(self):
        values = self.extractedContours.values()
        frames = []
        for xx in values:
            for v1 in xx:
                (x, y, w, h) = v1[1]
                v = v1[0]
                frame = np.zeros(shape=[self.yDim, self.xDim, 3], dtype=np.uint8)
                frame = imutils.resize(frame, width=512)
                frame[y:y+v.shape[0], x:x+v.shape[1]] = v
                frames.append(frame)
        return frames

