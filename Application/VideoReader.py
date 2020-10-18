
import multiprocessing
import cv2
from time import sleep
from queue import Queue
import threading
from Application.Config import Config


class VideoReader:
    listOfFrames = None
    w = 0
    h = 0

    def __init__(self, config, setOfFrames = None):
        videoPath = config["inputPath"]
        if videoPath is None:
            print("ERROR: Video reader needs a videoPath!")
            return None

        self.videoPath = videoPath
        self.lastFrame = 0
        #buffer = Queue([(frameNumber, frame), ])
        self.buffer = Queue(config["videoBufferLength"])
        self.vc = cv2.VideoCapture(videoPath)
        self.stopped = False
        self.getWH()
        if setOfFrames is not None:
            self.listOfFrames = sorted(setOfFrames)      

    def getWH(self):
        res, image = self.vc.read()
        self.w = image.shape[1]
        self.h = image.shape[0]
        return (self.w, self.h)

    def pop(self):
        return self.buffer.get(block=True)

    def get(self):
        return self.buffer[-1]

    def fillBuffer(self):
        if self.buffer.full():
            print("VideoReader::fillBuffer was called when buffer was full.")
        self.endFrame = int(self.vc.get(cv2.CAP_PROP_FRAME_COUNT))

        #self.endFrame = 10*60*30
        if self.listOfFrames is not None:
            self.thread = threading.Thread(target=self.readFramesByList, args=())
        else:
            self.thread = threading.Thread(target=self.readFrames, args=())
        self.thread.start()

    def stop(self):
        self.thread.join()
        self.vc.release()

    def readFrames(self):
        while self.lastFrame < self.endFrame:
            res, frame = self.vc.read()
            if res:
                self.buffer.put((self.lastFrame, frame))
            self.lastFrame += 1

        self.stopped = True

    
    def readFramesByList(self):
        self.vc.set(1, self.listOfFrames[0])
        self.lastFrame = self.listOfFrames[0]
        self.endFrame = self.listOfFrames[-1]

        while self.lastFrame < self.endFrame:
            if self.lastFrame in self.listOfFrames:
                res, frame = self.vc.read()
                if res:
                    self.buffer.put((self.lastFrame, frame))
                # since the list is sorted the first element is always the lowest relevant framenumber
                # [0,1,2,3,32,33,34,35,67,68,69]
                self.listOfFrames.pop(0)
                self.lastFrame += 1
            else:
                # if current Frame number is not in list of Frames, we can skip a few frames
                self.vc.set(1, self.listOfFrames[0])
                self.lastFrame = self.listOfFrames[0]
        
        self.stopped = True
    
    def videoEnded(self):
        if self.stopped and self.buffer.empty():
            return True
        else:
            return False

    def getFPS(self):
        return self.vc.get(cv2.CAP_PROP_FPS)
