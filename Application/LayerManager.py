import time
from multiprocessing.pool import ThreadPool

import cv2
import numpy as np

from Application.Classifiers.Classifier import Classifier
from Application.Config import Config
from Application.Exporter import Exporter
from Application.Layer import Layer
from Application.VideoReader import VideoReader


class LayerManager:
    def __init__(self, config, layers):
        self.data = {}
        self.layers = layers
        self.tolerance = config["tolerance"]
        self.ttolerance = config["ttolerance"]
        self.min_layer_length = config["minLayerLength"]
        self.max_layer_length = config["maxLayerLength"]
        self.resize_width = config["resizeWidth"]
        self.footage_path = config["inputPath"]
        self.config = config
        # self.classifier = Classifier()
        self.tags = []
        print("LayerManager constructed")

    def clean_layers(self):
        print("'Cleaning' Layers")
        print("Before deleting short layers ", len(self.layers))
        self.free_min()
        print("Before deleting long layers ", len(self.layers))
        self.free_max()
        self.sort_layers()
        print("Before deleting sparse layers ", len(self.layers))
        self.delete_sparse()
        print("after deleting sparse layers ", len(self.layers))
        #self.calcTimeOffset()

    def delete_sparse(self):
        to_delete = []
        for i, l in enumerate(self.layers):
            empty = l.bounds.count([])
            if empty / len(l) > 0.5:
                to_delete.append(i)

        for i, id in enumerate(to_delete):
            del self.layers[id - i]

    def free_min(self):
        self.data.clear()
        layers = []
        for l in self.layers:
            if len(l) > self.min_layer_length:
                layers.append(l)
        self.layers = layers

    def free_max(self):
        layers = []
        for l in self.layers:
            if len(l) < self.max_layer_length:
                layers.append(l)
        self.layers = layers

    def tag_layers(self):
        """Use classifieres the tag all Layers, by reading the contour content from the original video, then applying the classifier"""
        print("Tagging Layers")
        exporter = Exporter(self.config)
        start = time.time()
        for i, layer in enumerate(self.layers):
            print(f"{round(i/len(self.layers)*100,2)} {round((time.time() - start), 2)}")
            start = time.time()
            if len(layer.bounds[0]) == 0:
                continue
            list_of_frames = exporter.make_list_of_frames([layer])

            video_reader = VideoReader(self.config, list_of_frames)
            video_reader.fill_buffer()

            while not video_reader.video_ended():
                frame_count, frame = video_reader.pop()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                data = []
                for (x, y, w, h) in layer.bounds[frame_count - layer.start_frame]:
                    if x is None:
                        break
                    factor = video_reader.w / self.resize_width
                    x = int(x * factor)
                    y = int(y * factor)
                    w = int(w * factor)
                    h = int(h * factor)
                    data.append(np.copy(frame[y : y + h, x : x + w]))
                layer.data.append(data)
            tags = self.classifier.tagLayer(layer.data)
            print(tags)
            self.tags.append(tags)

            video_reader.thread.join()

    def sort_layers(self):
        self.layers.sort(key=lambda c: c.start_frame)

    def calc_time_offset(self):
        len_l = len(self.layers)
        for i in range(1, len(self.layers)):
            layer = self.layers[i]
            print(f"\r {i}/{len_l}", end="\r")
            overlap = True
            tries = 1
            while overlap:
                overlap = False
                for l in self.layers[:i:-1]:
                    if layer.timeOverlaps(l) and layer.spaceOverlaps(l):
                        overlap = True
                        break
                if overlap:
                    self.layers[i].export_offset += 20 * tries
                    tries += 1

                # if self.layers[i].export_offset >= 300000:
                #    break
