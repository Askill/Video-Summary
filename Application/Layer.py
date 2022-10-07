import cv2
import imutils
import numpy as np


class Layer:
    # bounds = [[(x,y,w,h), ],]

    start_frame = None
    last_frame = None
    length = None

    def __init__(self, start_frame, data, mask, config):
        """returns a Layer object

        Layers are collections of contours with a start_frame,
        which is the number of the frame the first contour of
        this layer was extraced from

        A Contour is a CV2 Contour, which is a y*x*3 rgb numpy array,
        but we only care about the corners of the contours.
        So we save the bounds (x,y,w,h) in bounds[] and the actual content in data[]
        """
        self.start_frame = start_frame
        self.last_frame = start_frame
        self.config = config
        self.data = []
        self.bounds = []
        self.masks = []
        self.stats = dict()
        self.export_offset = 0

        self.bounds.append([data])
        self.masks.append([mask])

    def add(self, frame_number, bound, mask):
        """Adds a bound to the Layer at the layer index which corresponds to the given framenumber"""
        index = frame_number - self.start_frame
        if index < 0:
            return
        if frame_number > self.last_frame:
            for i in range(frame_number - self.last_frame):
                self.bounds.append([])
                self.masks.append([])
            self.last_frame = frame_number

        if bound not in self.bounds[index]:
            self.bounds[index].append(bound)
            self.masks[index].append(mask)

    def get_length(self):
        return len(self) + self.export_offset

    def __len__(self):
        self.length = len(self.bounds)
        return self.length

    def space_overlaps(self, layer2):
        """Checks if there is an overlap in the bounds of current layer with given layer"""
        overlap = False
        max_len = min(len(layer2.bounds), len(self.bounds))
        bounds = self.bounds[:max_len]
        for b1s, b2s in zip(bounds[::10], layer2.bounds[:max_len:10]):
            for b1 in b1s:
                for b2 in b2s:
                    if self.contours_overlay((b1[0], b1[1] + b1[3]), (b1[0] + b1[2], b1[1]), (b2[0], b2[1] + b2[3]), (b2[0] + b2[2], b2[1])):
                        overlap = True
                        break
        return overlap

    def time_overlaps(self, layer2):
        """Checks for overlap in time between current and given layer"""
        s1 = self.export_offset
        e1 = self.last_frame - self.start_frame + self.export_offset
        s2 = layer2.export_offset
        e2 = layer2.last_frame - layer2.start_frame + layer2.export_offset

        if s2 >= s1 and s2 <= e1:
            return True
        elif s1 >= s2 and s1 <= e2:
            return True
        else:
            return False

    def contours_overlay(self, l1, r1, l2, r2):
        if l1[0] >= r2[0] or l2[0] >= r1[0]:
            return False
        if l1[1] <= r2[1] or l2[1] <= r1[1]:
            return False
        return True
