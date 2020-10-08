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
import matplotlib.pyplot as plt

class Analyzer:
    def __init__(self, videoPath):
        print("Analyzer constructed")
        data = self.readIntoMem(videoPath)

        vs = cv2.VideoCapture(videoPath)
        threashold = 13
        res, image = vs.read()
        firstFrame = None
        i = 0
        diff = []
        while res:
            res, frame = vs.read()
            if not res:
                break
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            if firstFrame is None:
                firstFrame = gray
                continue
            frameDelta = cv2.absdiff(gray, firstFrame)
            thresh = cv2.threshold(frameDelta, threashold, 255, cv2.THRESH_BINARY)[1]
            diff.append(np.count_nonzero(thresh))
            i+=1
            if i % (60*30) == 0:
                print("Minutes processed: ", i/(60*30))
                #print(diff)

        plt.plot(diff)
        plt.ylabel('some numbers')
        plt.show()