import multiprocessing
import os
import queue
import threading

import cv2


class VideoReader:
    listOfFrames = None
    w = None
    h = None

    def __init__(self, config, setOfFrames=None, multiprocess=False):
        videoPath = config["inputPath"]
        if videoPath is None:
            raise Exception("ERROR: Video reader needs a videoPath!")
        self.videoPath = videoPath
        self.lastFrame = 0
        # buffer data struct:
        # buffer = Queue([(frameNumber, frame), ])
        self.multiprocess = multiprocess
        if multiprocess:
            self.buffer = multiprocessing.Manager().Queue(config["videoBufferLength"])
        else:
            self.buffer = queue.Queue(config["videoBufferLength"])
        self.stopped = False
        self.getWH()
        self.calcFPS()
        self.calcLength()
        self.calcStartTime()
        if setOfFrames is not None:
            self.listOfFrames = sorted(setOfFrames)

    def __enter__(self):
        self.fillBuffer()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def stop(self):
        self.thread.join()

    def pop(self):
        frameNumber, frame = self.buffer.get(block=True)
        if frame is None:
            self.stopped = True
        return frameNumber, frame

    def fillBuffer(self, listOfFrames=None):
        self.endFrame = int(cv2.VideoCapture(self.videoPath).get(cv2.CAP_PROP_FRAME_COUNT))
        if listOfFrames is not None:
            self.listOfFrames = listOfFrames

        if self.multiprocess:
            if self.listOfFrames is not None:
                self.thread = multiprocessing.Process(target=self.readFramesByList, args=())
            else:
                self.thread = multiprocessing.Process(target=self.readFrames, args=())
        else:
            if self.listOfFrames is not None:
                self.thread = threading.Thread(target=self.readFramesByList, args=())
            else:
                self.thread = threading.Thread(target=self.readFrames, args=())
        self.thread.start()

    def readFrames(self):
        """Reads video from start to finish"""
        self.vc = cv2.VideoCapture(self.videoPath)
        while self.lastFrame < self.endFrame:
            res, frame = self.vc.read()
            if res:
                self.buffer.put((self.lastFrame, frame))
            self.lastFrame += 1
        self.buffer.put((self.lastFrame, None))

    def readFramesByList(self):
        """Reads all frames from a list of frame numbers"""
        self.vc = cv2.VideoCapture(self.videoPath)
        self.vc.set(1, self.listOfFrames[0])
        self.lastFrame = self.listOfFrames[0]
        self.endFrame = self.listOfFrames[-1]

        while self.lastFrame < self.endFrame:
            if self.lastFrame in self.listOfFrames:
                res, frame = self.vc.read()
                if res:
                    self.buffer.put((self.lastFrame, frame))
                else:
                    print("Couldn't read Frame")
                # since the list is sorted the first element is always the lowest relevant framenumber
                # [0,1,2,3,32,33,34,35,67,68,69]
                self.listOfFrames.pop(0)
                self.lastFrame += 1
            else:
                # if current Frame number is not in list of Frames, we can skip a few frames
                self.vc.set(1, self.listOfFrames[0])
                self.lastFrame = self.listOfFrames[0]
        self.buffer.put((self.lastFrame, None))

    def videoEnded(self):
        if self.stopped and self.buffer.empty():
            return True
        else:
            return False

    def calcFPS(self):
        self.fps = cv2.VideoCapture(self.videoPath).get(cv2.CAP_PROP_FPS)

    def getFPS(self):
        if self.fps is None:
            self.calcFPS()
        return self.fps

    def calcLength(self):
        fc = int(cv2.VideoCapture(self.videoPath).get(cv2.CAP_PROP_FRAME_COUNT))
        self.length = fc / self.getFPS()

    def getLength(self):
        if self.length is None:
            self.calcLength()
        return self.length

    def calcStartTime(self):
        starttime = os.stat(self.videoPath).st_mtime
        length = self.getLength()
        starttime = starttime - length
        self.starttime = starttime

    def getStartTime(self):
        return self.starttime

    def getWH(self):
        """get width and height"""
        vc = cv2.VideoCapture(self.videoPath)
        if self.w is None or self.h is None:
            res, image = vc.read()
            self.w = image.shape[1]
            self.h = image.shape[0]

        return (self.w, self.h)
