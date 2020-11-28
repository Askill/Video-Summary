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
from Application.VideoReader import VideoReader
from queue import Queue
import threading

from Application.Config import Config

class ContourExtractor:

    #extracedContours = {frame_number: [(contour, (x,y,w,h)), ...], }
    # dict with frame numbers as keys and the contour bounds of every contour for that frame 

    def getExtractedContours(self):
        return self.extractedContours

    def getExtractedMasks(self):
        return self.extractedMasks


    def __init__(self, config):
        self.frameBuffer = Queue(16)
        self.extractedContours = dict()
        self.extractedMasks = dict()
        self.min_area = config["min_area"]
        self.max_area = config["max_area"]
        self.threashold = config["threashold"]
        self.resizeWidth = config["resizeWidth"]
        self.videoPath = config["inputPath"]
        self.xDim = 0
        self.yDim = 0       
        self.config = config
        self.diff = []
        self.lastFrames = None
        self.averages = dict()

        print("ContourExtractor initiated")

    def extractContours(self):      
        videoReader = VideoReader(self.config)    
        videoReader.fillBuffer()

        threads = self.config["videoBufferLength"]
        self.start = time.time()
        # start a bunch of frames and let them read from the video reader buffer until the video reader reaches EOF
        with ThreadPool(threads) as pool:
            while not videoReader.videoEnded():
                if videoReader.buffer.qsize() == 0:
                    time.sleep(.5)

                tmpData = [videoReader.pop() for i in range(0, videoReader.buffer.qsize())]
                self.computeMovingAverage(tmpData)
                #pool.map(self.getContours, tmpData)
                for data in tmpData:
                    self.getContours(data)
                frameCount = tmpData[-1][0]

        videoReader.thread.join()
        return self.extractedContours, self.extractedMasks
    
    def getContours(self, data):
        frameCount, frame = data
        # wait for the reference frame, which is calculated by averaging some revious frames
        while frameCount not in self.averages:
            time.sleep(0.1)
        firstFrame = self.averages.pop(frameCount, None)
       
        if frameCount % (60*30) == 0:
            print(f" \r {frameCount/(60*30)} Minutes processed in {round((time.time() - self.start), 2)} each", end='\r')
            self.start = time.time()

        gray = self.prepareFrame(frame)
        frameDelta = cv2.absdiff(gray, firstFrame)
        thresh = cv2.threshold(frameDelta, self.threashold, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        thresh = cv2.dilate(thresh, None, iterations=10)
        #cv2.imshow("changes x", thresh)
        #cv2.waitKey(10) & 0XFF
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.diff.append(np.count_nonzero(thresh))
        cnts = imutils.grab_contours(cnts)

        contours = []
        masks = []
        for c in cnts:
            ca = cv2.contourArea(c)
            (x, y, w, h) = cv2.boundingRect(c)
            #ca = (x+w)*(y+h)
            if ca < self.min_area or ca > self.max_area:
                continue

            contours.append((x, y, w, h))
            masks.append(np.packbits(np.copy(thresh[y:y+h,x:x+w]), axis=0))
            
       
            
        if len(contours) != 0 and contours is not None: 
            # this should be thread safe
            self.extractedContours[frameCount] = contours
            self.extractedMasks[frameCount] =  masks

    def prepareFrame(self, frame):
        frame = imutils.resize(frame, width=self.resizeWidth)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        return gray

    def computeMovingAverage(self, frames):
        avg = []
        averageFrames = self.config["avgNum"]

        nth = int(averageFrames/3) # only take /x  x frames to average
        if frames[0][0] < averageFrames:
            frame = frames[0][1]
            frame = self.prepareFrame(frame)
            for j in range(0, len(frames)):
                frameNumber, _ = frames[j] 
                self.averages[frameNumber] = frame
                # put last x frames into a buffer
            self.lastFrames = frames[-averageFrames:] 
            return

        if self.lastFrames is not None:
            frames = self.lastFrames + frames 

        tmp = [[j, frames, averageFrames] for j in range(averageFrames, len(frames))]
        with ThreadPool(16) as pool:
            pool.map(self.averageDaFrames, tmp)

        self.lastFrames = frames[-averageFrames:] 


    def averageDaFrames(self, dat):
        j, frames, averageFrames = dat
        frameNumber, frame = frames[j]
        frame = self.prepareFrame(frame)
        
        avg = frame/averageFrames
        for jj in range(0,averageFrames-1):
            avg += self.prepareFrame(frames[j-jj][1])/averageFrames
        self.averages[frameNumber] = np.array(np.round(avg), dtype=np.uint8)
        #self.averages[frameNumber] = self.prepareFrame(frames[j-averageFrames - 1][1])
