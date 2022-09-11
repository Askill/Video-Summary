import multiprocessing
import os
import queue
import threading

import cv2


class VideoReader:
    list_of_frames = None
    w = None
    h = None

    def __init__(self, config, set_of_frames=None, multiprocess=False):
        video_path = config["inputPath"]
        if video_path is None:
            raise Exception("ERROR: Video reader needs a video_path!")
        self.video_path = video_path
        self.last_frame = 0
        # buffer data struct:
        # buffer = Queue([(frameNumber, frame), ])
        self.multiprocess = multiprocess
        if multiprocess:
            self.buffer = multiprocessing.Manager().Queue(config["videoBufferLength"])
        else:
            self.buffer = queue.Queue(config["videoBufferLength"])
        self.stopped = False
        self.get_wh()
        self.calc_fps()
        self.calc_length()
        self.calc_start_time()
        if set_of_frames is not None:
            self.list_of_frames = sorted(set_of_frames)

    def __enter__(self):
        self.fill_buffer()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def stop(self):
        self.thread.join()

    def pop(self):
        frame_number, frame = self.buffer.get(block=True)
        if frame is None:
            self.stopped = True
        return frame_number, frame

    def fill_buffer(self, list_of_frames=None):
        self.end_frame = int(cv2.VideoCapture(self.video_path).get(cv2.CAP_PROP_FRAME_COUNT))
        if list_of_frames is not None:
            self.list_of_frames = list_of_frames

        if self.multiprocess:
            if self.list_of_frames is not None:
                self.thread = multiprocessing.Process(target=self.read_frames_by_list, args=())
            else:
                self.thread = multiprocessing.Process(target=self.read_frames, args=())
        else:
            if self.list_of_frames is not None:
                self.thread = threading.Thread(target=self.read_frames_by_list, args=())
            else:
                self.thread = threading.Thread(target=self.read_frames, args=())
        self.thread.start()

    def read_frames(self):
        """Reads video from start to finish"""
        self.vc = cv2.VideoCapture(self.video_path)
        while self.last_frame < self.end_frame:
            res, frame = self.vc.read()
            if res:
                self.buffer.put((self.last_frame, frame))
            self.last_frame += 1
        self.buffer.put((self.last_frame, None))

    def read_frames_by_list(self):
        """Reads all frames from a list of frame numbers"""
        self.vc = cv2.VideoCapture(self.video_path)
        self.vc.set(1, self.list_of_frames[0])
        self.last_frame = self.list_of_frames[0]
        self.end_frame = self.list_of_frames[-1]

        while self.last_frame < self.end_frame:
            if self.last_frame in self.list_of_frames:
                res, frame = self.vc.read()
                if res:
                    self.buffer.put((self.last_frame, frame))
                else:
                    print("Couldn't read Frame")
                # since the list is sorted the first element is always the lowest relevant framenumber
                # [0,1,2,3,32,33,34,35,67,68,69]
                self.list_of_frames.pop(0)
                self.last_frame += 1
            else:
                # if current Frame number is not in list of Frames, we can skip a few frames
                self.vc.set(1, self.list_of_frames[0])
                self.last_frame = self.list_of_frames[0]
        self.buffer.put((self.last_frame, None))

    def video_ended(self):
        if self.stopped and self.buffer.empty():
            return True
        else:
            return False

    def calc_fps(self):
        self.fps = cv2.VideoCapture(self.video_path).get(cv2.CAP_PROP_FPS)

    def get_fps(self):
        if self.fps is None:
            self.calc_fps()
        return self.fps

    def calc_length(self):
        fc = int(cv2.VideoCapture(self.video_path).get(cv2.CAP_PROP_FRAME_COUNT))
        self.length = fc / self.get_fps()

    def get_length(self):
        if self.length is None:
            self.calc_length()
        return self.length

    def calc_start_time(self):
        starttime = os.stat(self.video_path).st_mtime
        length = self.get_length()
        starttime = starttime - length
        self.starttime = starttime

    def get_start_time(self):
        return self.starttime

    def get_wh(self):
        """get width and height"""
        vc = cv2.VideoCapture(self.video_path)
        if self.w is None or self.h is None:
            res, image = vc.read()
            self.w = image.shape[1]
            self.h = image.shape[0]

        return (self.w, self.h)
