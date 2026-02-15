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

    def get_extracted_contours(self):
        return self.extracted_contours

    def get_extracted_masks(self):
        return self.extracted_masks

    def __init__(self, config):
        self.frame_buffer = Queue(16)
        self.extracted_contours = dict()
        self.extracted_masks = dict()
        self.min_area = config["min_area"]
        self.max_area = config["max_area"]
        self.threshold = config["threshold"]
        self.resize_width = config["resizeWidth"]
        self.video_path = config["inputPath"]
        self.x_dim = 0
        self.y_dim = 0
        self.config = config
        self.last_frames = None
        self.averages = dict()

        print("ContourExtractor initiated")

    def extract_contours(self):
        self.start = time.time()
        with VideoReader(self.config) as videoReader:
            self.fps = videoReader.get_fps()
            self.length = videoReader.get_length()

            with ThreadPool(os.cpu_count()) as pool:
                while True:
                    while not videoReader.video_ended() and videoReader.buffer.qsize() == 0:
                        time.sleep(0.5)

                    tmp_data = [videoReader.pop() for i in range(0, videoReader.buffer.qsize())]
                    if videoReader.video_ended():
                        break
                    pool.map(self.compute_moving_Average, (tmp_data,))
                    pool.map(self.get_contours, tmp_data)

        return self.extracted_contours, self.extracted_masks

    def get_contours(self, data):
        frame_count, frame = data
        # wait for the reference frame, which is calculated by averaging some revious frames
        while frame_count not in self.averages:
            time.sleep(0.1)
        first_frame = self.averages.pop(frame_count, None)

        if frame_count % (10 * self.fps) == 1:
            print(
                f" \r \033[K {round((frame_count/self.fps)*100/self.length, 2)} % processed in {round(time.time() - self.start, 2)}s",
                end="\r",
            )

        gray = self.prepare_frame(frame)
        frame_delta = cv2.absdiff(gray, first_frame)
        thresh = cv2.threshold(frame_delta, self.threshold, 255, cv2.THRESH_BINARY)[1]
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
            x, y, w, h = cv2.boundingRect(c)
            if ca < self.min_area or ca > self.max_area:
                continue
            contours.append((x, y, w, h))
            # the mask has to be packed like this, since np doesn't have a bit array,
            # meaning every bit in the mask would take up 8bits, which migth be too much
            masks.append(np.packbits(np.copy(thresh[y : y + h, x : x + w]), axis=0))

        if len(contours) != 0 and contours is not None:
            # this should be thread safe
            self.extracted_contours[frame_count] = contours
            self.extracted_masks[frame_count] = masks

    def prepare_frame(self, frame):
        frame = imutils.resize(frame, width=self.resize_width)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        return gray

    def compute_moving_Average(self, frames):
        average_frames = self.config["avgNum"]

        if frames[0][0] < average_frames:
            frame = frames[0][1]
            frame = self.prepare_frame(frame)
            for j in range(0, len(frames)):
                frame_number, _ = frames[j]
                self.averages[frame_number] = frame
                # put last x frames into a buffer
            self.last_frames = frames[-average_frames:]
            return

        if self.last_frames is not None:
            frames = self.last_frames + frames

        tmp = [[j, frames, average_frames] for j in range(average_frames, len(frames))]
        with ThreadPool(int(os.cpu_count())) as pool:
            pool.map(self.average_da_frames, tmp)

        self.last_frames = frames[-average_frames:]

    def average_da_frames(self, dat):
        j, frames, average_frames = dat
        frame_number, frame = frames[j]
        frame = self.prepare_frame(frame)

        avg = frame / average_frames
        for jj in range(0, average_frames - 1):
            avg += self.prepare_frame(frames[j - jj][1]) / average_frames
        self.averages[frame_number] = np.array(np.round(avg), dtype=np.uint8)
