import os
import time
from multiprocessing import Pool, Process, Queue
from multiprocessing.pool import ThreadPool
from queue import Queue
from threading import Thread, activeCount

import cv2
import imutils
import numpy as np

from Application.Config import Config
from Application.VideoReader import VideoReader


class ContourExtractor:
    # extracedContours = {frame_number: [(contour, (x,y,w,h)), ...], }
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
        self.lastFrames = None
        self.averages = dict()

        print("ContourExtractor initiated")

    def extractContours(self):
        self.start = time.time()
        with VideoReader(self.config) as videoReader:
            self.fps = videoReader.getFPS()
            self.length = videoReader.getLength()

            with ThreadPool(2) as pool:
                while True:
                    while not videoReader.videoEnded() and videoReader.buffer.qsize() == 0:
                        time.sleep(0.5)

                    tmpData = [videoReader.pop() for i in range(0, videoReader.buffer.qsize())]
                    if videoReader.videoEnded():
                        break
                    pool.map(self.computeMovingAverage, (tmpData,))
                    pool.map(self.async2, (tmpData,))

        return self.extractedContours, self.extractedMasks

    def async2(self, tmpData):
        with ThreadPool(os.cpu_count()) as pool2:
            pool2.map(self.getContours, tmpData)

    def getContours(self, data):
        frameCount, frame = data
        # wait for the reference frame, which is calculated by averaging some revious frames
        while frameCount not in self.averages:
            time.sleep(0.1)
        firstFrame = self.averages.pop(frameCount, None)

        if frameCount % (10 * self.fps) == 1:
            print(
                f" \r \033[K {round((frameCount/self.fps)*100/self.length, 2)} % processed in {round(time.time() - self.start, 2)}s",
                end="\r",
            )

        gray = self.prepareFrame(frame)
        frameDelta = cv2.absdiff(gray, firstFrame)
        thresh = cv2.threshold(frameDelta, self.threashold, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        thresh = cv2.dilate(thresh, None, iterations=10)
        # cv2.imshow("changes x", thresh)
        # cv2.waitKey(10) & 0XFF
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        contours = []
        masks = []
        for c in cnts:
            ca = cv2.contourArea(c)
            (x, y, w, h) = cv2.boundingRect(c)
            if ca < self.min_area or ca > self.max_area:
                continue
            contours.append((x, y, w, h))
            # the mask has to be packed like this, since np doesn't have a bit array,
            # meaning every bit in the mask would take up 8bits, which migth be too much
            masks.append(np.packbits(np.copy(thresh[y : y + h, x : x + w]), axis=0))

        if len(contours) != 0 and contours is not None:
            # this should be thread safe
            self.extractedContours[frameCount] = contours
            self.extractedMasks[frameCount] = masks

    def prepareFrame(self, frame):
        frame = imutils.resize(frame, width=self.resizeWidth)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        return gray

    def computeMovingAverage(self, frames):
        averageFrames = self.config["avgNum"]

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
        with ThreadPool(int(os.cpu_count())) as pool:
            pool.map(self.averageDaFrames, tmp)

        self.lastFrames = frames[-averageFrames:]

    def averageDaFrames(self, dat):
        j, frames, averageFrames = dat
        frameNumber, frame = frames[j]
        frame = self.prepareFrame(frame)

        avg = frame / averageFrames
        for jj in range(0, averageFrames - 1):
            avg += self.prepareFrame(frames[j - jj][1]) / averageFrames
        self.averages[frameNumber] = np.array(np.round(avg), dtype=np.uint8)
