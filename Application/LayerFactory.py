import os
from multiprocessing.pool import ThreadPool

import numpy as np

from Application.Config import Config
from Application.Exporter import Exporter
from Application.Layer import Layer
from Application.VideoReader import VideoReader


class LayerFactory:
    def __init__(self, config, data=None):
        self.data = {}
        self.layers = []
        self.tolerance = config["tolerance"]
        self.ttolerance = config["ttolerance"]
        self.min_layer_length = config["minLayerLength"]
        self.max_layer_length = config["maxLayerLength"]
        self.resize_width = config["resizeWidth"]
        self.footage_path = config["inputPath"]
        self.config = config
        print("LayerFactory constructed")
        self.data = data
        if data is not None:
            self.extract_layers(data)

    def extract_layers(self, data, mask_arr):
        """Bundle given contours together into Layer Objects"""

        frame_number = min(data)
        contours = data[frame_number]
        masks = mask_arr[frame_number]

        for contour, mask in zip(contours, masks):
            mask = np.unpackbits(mask, axis=0)
            self.layers.append(Layer(frame_number, contour, mask, self.config))

        self.old_layer_i_ds = []

        with ThreadPool(os.cpu_count()) as pool:
            for frame_number in sorted(data.keys()):
                contours = data[frame_number]
                masks = mask_arr[frame_number]
                masks = [np.unpackbits(mask, axis=0) for mask, contours in zip(masks, contours)]
                if frame_number % 100 == 0:
                    print(
                        f" {int(round(frame_number/max(data.keys()), 2)*100)}% done with Layer extraction {len(self.layers)} Layers",
                        end="\r",
                    )

                tmp = [[frame_number, contour, mask] for contour, mask in zip(contours, masks)]
                # pool.map(self.getLayers, tmp)
                for x in tmp:
                    self.get_layers(x)

        # self.joinLayers()
        return self.layers

    def get_layers(self, data):
        frame_number = data[0]
        bounds = data[1]
        mask = data[2]
        (x, y, w, h) = bounds
        tol = self.tolerance

        found_layer_i_ds = set()
        for i, layer in enumerate(self.layers):
            if frame_number - layer.last_frame > self.ttolerance:
                continue

            last_xframes = min(40, len(layer))
            last_bounds = [bound for bounds in layer.bounds[-last_xframes:] for bound in bounds]

            for j, bounds in enumerate(sorted(last_bounds, reverse=True)):
                if bounds is None:
                    break
                (x2, y2, w2, h2) = bounds
                if self.contours_overlay((x - tol, y + h + tol), (x + w + tol, y - tol), (x2, y2 + h2), (x2 + w2, y2)):
                    layer.add(frame_number, (x, y, w, h), mask)
                    found_layer_i_ds.add(i)
                    break

        found_layer_i_ds = sorted(list(found_layer_i_ds))
        if len(found_layer_i_ds) == 0:
            self.layers.append(Layer(frame_number, (x, y, w, h), mask, self.config))
        if len(found_layer_i_ds) > 1:
            self.merge_layers(found_layer_i_ds)

    def merge_layers(self, found_layer_i_ds):
        layers = self.get_layers_by_id(found_layer_i_ds)
        merged_layers = layers[0]
        for layer in layers[1:]:
            for i, (contours, masks) in enumerate(zip(layer.bounds, layer.masks)):
                for contour, mask in zip(contours, masks):
                    merged_layers.add(layer.start_frame + i, contour, mask)

        for i, id in enumerate(found_layer_i_ds):
            del self.layers[id - i]

        self.layers.append(merged_layers)

    def join_layers(self):
        self.layers.sort(key=lambda c: c.start_frame)
        min_frame = self.get_min_start(self.layers)
        max_frame = self.get_max_end(self.layers)

        for i in range(min_frame, max_frame):
            p_l, indexes = self.get_possible_layers(i)
            if len(p_l) <= 1:
                continue
            merge = set()
            inner_max = self.get_max_end(p_l)
            for x in range(self.get_min_start(p_l), inner_max):
                for lc, l in enumerate(p_l):
                    if l.start_frame < x or l.last_frame > x:
                        continue
                    for lc2, l2 in enumerate(p_l):
                        if lc2 == lc:
                            continue
                        for cnt in l.bounds[x - l.start_frame]:
                            for cnt2 in l2.bounds[x - l2.start_frame]:
                                if self.contours_overlay(cnt, cnt2):
                                    merge.add(indexes[lc])
                                    merge.add(indexes[lc2])
            merge = list(merge)
            if len(merge) > 1:
                self.merge_layers(merge)
            i = inner_max

    def get_possible_layers(self, t):
        ret = []
        ii = []
        for i, layer in enumerate(self.layers):
            if layer.start_frame <= t and layer.last_frame <= t:
                ret.append(layer)
                ii.append(i)
        return (ret, ii)

    def get_min_start(self, layers):
        min_frame = layers[0].start_frame
        for l in layers:
            if l.start_frame < min_frame:
                min_frame = l.start_frame
        return min_frame

    def get_max_end(self, layers):
        max_frame = layers[0].last_frame
        for l in layers:
            if l.last_frame < max_frame:
                max_frame = l.last_frame
        return max_frame

    def contours_overlay(self, l1, r1, l2, r2):
        if l1[0] >= r2[0] or l2[0] >= r1[0]:
            return False
        if l1[1] <= r2[1] or l2[1] <= r1[1]:
            return False
        return True

    def get_layers_by_id(self, found_layer_i_ds):
        layers = []
        for layer_id in found_layer_i_ds:
            layers.append(self.layers[layer_id])

        layers.sort(key=lambda c: c.start_frame)
        return layers
