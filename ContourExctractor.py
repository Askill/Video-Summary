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
from threading import Thread
from multiprocessing import Queue, Process, Pool
from multiprocessing.pool import ThreadPool
import concurrent.futures
from VideoReader import VideoReader
from queue import Queue
import threading
from multiprocessing.pool import ThreadPool
from Config import Config

class ContourExtractor:

    #X = {frame_number: [(contour, (x,y,w,h)), ...], }


    def getextractedContours(self):
        return self.extractedContours

    def __init__(self, config):
        self.frameBuffer = Queue(16)
        self.extractedContours = dict()
        self.min_area = config["min_area"]
        self.max_area = config["max_area"]
        self.threashold = config["threashold"]
        self.resizeWidth = config["resizeWidth"]
        self.videoPath = config["inputPath"]
        self.xDim = 0
        self.yDim = 0       
        self.config = config

        print("ContourExtractor initiated")

    def extractContours(self):
        extractedContours = dict()        
        videoReader = VideoReader(self.config)
        self.xDim = videoReader.w
        self.yDim = videoReader.h
         
        videoReader.fillBuffer()
        frameCount, frame = videoReader.pop()
        
        #init compare image
        frame = imutils.resize(frame, width=self.resizeWidth)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
        #gray = np.asarray(gray[:,:,1]/2 + gray[:,:,2]/2).astype(np.uint8) 
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        self.firstFrame = gray

        threads = 16
        start = time.time()
        with ThreadPool(threads) as pool:
            while not videoReader.videoEnded():
                #FrameCount, frame = videoReader.pop()
                if frameCount % (60*30) == 0:
                    print(f"Minutes processed: {frameCount/(60*30)} in {round((time.time() - start), 2)} each")
                    start = time.time()

                if videoReader.buffer.qsize() == 0:
                    time.sleep(.5)

                tmpData = [videoReader.pop() for i in range(0, videoReader.buffer.qsize())]
                frameCount = tmpData[-1][0]
                pool.map(self.getContours, tmpData)

        videoReader.thread.join()
        return self.extractedContours
            
    def getContours(self, data):
        frameCount, frame = data
        firstFrame = self.firstFrame
        frame = imutils.resize(frame, width=self.resizeWidth)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        frameDelta = cv2.absdiff(gray, firstFrame)
        thresh = cv2.threshold(frameDelta, self.threashold, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        thresh = cv2.dilate(thresh, None, iterations=4)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        contours = []
        for c in cnts:
            ca = cv2.contourArea(c)
            if ca < self.min_area or ca > self.max_area:
                continue
            (x, y, w, h) = cv2.boundingRect(c)

            contours.append((x, y, w, h))
        
        if len(contours) != 0 and contours is not None: 
            # this should be thread safe
            self.extractedContours[frameCount] = contours

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

