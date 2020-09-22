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

class ContourExtractor:

    #X = {frame_number: contours, }
    extractedContours = dict()

    def __init__(self, videoPath):
        print("ContourExtractror initiated")
        print(videoPath)

        min_area = 100
        max_area = 30000

        threashold = 10

        # initialize the first frame in the video stream
        vs = cv2.VideoCapture(videoPath)

        res = vs.read()[0]
        firstFrame = None
        # loop over the frames of the video
        frameCount = 0
        while res:

            res, frame = vs.read()

            # resize the frame, convert it to grayscale, and blur it
            if frame is None:
                return
            #frame = imutils.resize(frame, width=500)
            cv2.imshow( "frame", frame )  
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (31, 31), 0)

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

            # loop over the contours
            for c in cnts:
                if cv2.contourArea(c) < min_area or cv2.contourArea(c) > max_area:
                    continue

                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"

            self.extractedContours[frameCount] = cnts
            frameCount += 1

            #cv2.imshow( "annotated", frame )  

            #cv2.waitKey(10) & 0XFF
    
    def displayContours(self):
        
        values = self.extractedContours.values()
        frame = np.zeros(shape=[1080, 1920, 3], dtype=np.uint8)
        #frame = imutils.resize(frame, width=500)

        for x in values:
            for v in x:
                (x, y, w, h) = cv2.boundingRect(v)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("changes overlayed", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

