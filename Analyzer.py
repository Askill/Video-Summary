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
from VideoReader import VideoReader
from multiprocessing.pool import ThreadPool
import imutils


class Analyzer:
    
    def __init__(self, config):
        print("Analyzer constructed")
        videoReader = VideoReader(config)
        videoReader.fillBuffer()
        self.config = config
        self.avg = imutils.resize(np.zeros((videoReader.h,videoReader.w,3),np.float), width=config["resizeWidth"])
        self.end = videoReader.endFrame
        self.c = 0
        start = time.time()
        fak = 10
        while not videoReader.videoEnded():
            self.c, frame = videoReader.pop()
            if not self.c%fak == 0:
                continue
            if videoReader.endFrame - self.c <= fak:
                break
            frame = imutils.resize(frame, width=self.config["resizeWidth"])
            

            self.avg += frame.astype(np.float)/(self.end/fak)
            if self.c%(1800*6) == 0:
                print(f"{self.c/(60*30)} Minutes processed in {round((time.time() - start), 2)} each")
                start = time.time()

        #print("done")
        videoReader.thread.join()      
        self.avg = np.array(np.round(self.avg), dtype=np.uint8)
        #return self.avg
        cv2.imshow("changes overlayed", self.avg)
        cv2.waitKey(10) & 0XFF



    def average(self, frame):
        frame = imutils.resize(frame[1], width=self.config["resizeWidth"])
        self.avg += frame.astype(np.float)/(self.end/5)


