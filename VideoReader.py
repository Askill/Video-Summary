
import multiprocessing
import cv2
from time import sleep
from queue import Queue
import threading
class VideoReader:

    #buffer = [(frameNumber, frame)]

    def __init__(self, videoPath):
        if videoPath is None:
            print("Video reader needs a videoPath!")
            return None

        self.videoPath = videoPath
        self.lastFrame = 0
        self.buffer = Queue(16)
        self.vc = cv2.VideoCapture(videoPath)
        self.stopped = False
        res, image = self.vc.read()
        self.w = image.shape[1]
        self.h = image.shape[0]
        
        print(f"Video reader startet with buffer length of 16")
        

    def pop(self):
        return self.buffer.get(block=True)

    def get(self):
        return self.buffer[-1]

    def fillBuffer(self):
        if self.buffer.full():
            print("VideoReader::fillBuffer was called when buffer was full.")
        self.endFrame = int(self.vc.get(cv2.CAP_PROP_FRAME_COUNT))
        self.endFrame = 10*60*30
        self.thread = threading.Thread(target=self.readFrames, args=())
        self.thread.start()

    def stop(self):
        self.thread.join()
        self.vc.release()

    def readFrames(self):
        while self.lastFrame < self.endFrame:
            if not self.buffer.full():
                res, frame = self.vc.read()
                if res:
                    self.buffer.put((self.lastFrame, frame))
                self.lastFrame += 1
            else:
                sleep(0.5)
        self.stopped = True
    
    def videoEnded(self):
        if self.stopped:
            return True
        else:
            return False
        





        


