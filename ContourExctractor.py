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
from VideoReader import VideoReader

class ContourExtractor:

    #X = {frame_number: [(contour, (x,y,w,h)), ...], }
    extractedContours = dict()
    min_area = 100
    max_area = 1000
    threashold = 13
    xDim = 0
    yDim = 0

    def getextractedContours(self):
        return self.extractedContours

    def __init__(self):
        print("ContourExtractor initiated")

    def extractContours(self, videoPath, resizeWidth):
        firstFrame = None
        extractedContours = dict()        
        videoReader = VideoReader(videoPath)
        self.xDim = videoReader.w
        self.yDim = videoReader.h
        videoReader.fillBuffer()

        while not videoReader.videoEnded():
            frameCount, frame = videoReader.pop()
            if frameCount % (60*30) == 0:
                print("Minutes processed: ", frameCount/(60*30))
            
            if frame is None:
                print("ContourExtractor: frame was None")
                continue

            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=resizeWidth)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # if the first frame is None, initialize it
            if firstFrame is None:
                #gray = np.asarray(gray[:,:,1]/2 + gray[:,:,2]/2).astype(np.uint8)       
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                firstFrame = gray
                continue
            x = self.getContours(gray, firstFrame)
            if x is not None:
                extractedContours[frameCount] = x

        print("done")
        videoReader.thread.join()
        self.extractedContours = extractedContours
        return extractedContours
            
    def getContours(self, gray, firstFrame):
              
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

        if len(contours) != 0 and contours is not None: 
            return contours


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

