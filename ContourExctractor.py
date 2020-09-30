from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import os
import numpy as np
import traceback
import _thread
import imageio
import numpy as np

class ContourExtractor:

    #X = {frame_number: [(contour, (x,y,w,h)), ...], }
    extractedContours = dict()
    min_area = 100
    max_area = 50000
    threashold = 12
    xDim = 0
    yDim = 0

    def getextractedContours(self):
        return self.extractedContours

    def __init__(self):
        print("ContourExtractor initiated")

    def extractContours(self, videoPath):
        min_area = self.min_area
        max_area = self.max_area
        threashold = self.threashold

        # initialize the first frame in the video stream
        vs = cv2.VideoCapture(videoPath)

        res, image = vs.read()
        self.xDim = image.shape[1]
        self.yDim = image.shape[0]
        firstFrame = None
        # loop over the frames of the video
        frameCount = 0
        extractedContours = dict()
        while res:
            res, frame = vs.read()
            # resize the frame, convert it to grayscale, and blur it
            if frame is None:
                print("ContourExtractor: frame was None")
                break

            frame = imutils.resize(frame, width=500)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            # if the first frame is None, initialize it
            if firstFrame is None:
                firstFrame = gray
                continue

            frameDelta = cv2.absdiff(gray, firstFrame)
            thresh = cv2.threshold(frameDelta, threashold, 255, cv2.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            thresh = cv2.dilate(thresh, None, iterations=3)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            contours = []
            for c in cnts:
                ca = cv2.contourArea(c)
                if ca < min_area or ca > max_area:
                    continue
                (x, y, w, h) = cv2.boundingRect(c)
                #print((x, y, w, h))
                contours.append((frame[y:y+h, x:x+w], (x, y, w, h)))
                
                #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if len(contours) != 0:
                extractedContours[frameCount] = contours
            frameCount += 1

            #cv2.imshow( "annotated", frame )  
            #cv2.waitKey(10) & 0XFF
        self.extractedContours = extractedContours
            
    
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

