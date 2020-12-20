from Application.Layer import Layer
from Application.Config import Config
from Application.VideoReader import VideoReader
from Application.Exporter import Exporter
from multiprocessing.pool import ThreadPool
import cv2
import numpy as np
import copy


class LayerFactory:
    def __init__(self, config, data=None):
        self.data = {}
        self.layers = []
        self.tolerance = config["tolerance"]
        self.ttolerance = config["ttolerance"]
        self.minLayerLength = config["minLayerLength"]
        self.maxLayerLength = config["maxLayerLength"]
        self.resizeWidth = config["resizeWidth"]
        self.footagePath = config["inputPath"]
        self.config = config
        #print("LayerFactory constructed")
        self.data = data
        if data is not None:
            self.extractLayers(data)

    def extractLayers(self, data, maskArr):
        '''Bundle given contours together into Layer Objects'''

        frameNumber = min(data)
        contours = data[frameNumber]
        masks = maskArr[frameNumber]

        for contour, mask in zip(contours, masks):
            mask = np.unpackbits(mask, axis=0)
            self.layers.append(Layer(frameNumber, contour, mask, self.config))

        self.oldLayerIDs = []

        with ThreadPool(self.config["lf_threads"]) as pool:
            for frameNumber in sorted(data.keys()):
                contours = data[frameNumber]
                masks = maskArr[frameNumber]
                masks = [np.unpackbits(mask, axis=0)
                         for mask, contours in zip(masks, contours)]
                if frameNumber % 100 == 0:
                    print(
                        f" {int(round(frameNumber/max(data.keys()), 2)*100)}% done with Layer extraction {len(self.layers)} Layers", end='\r')

                tmp = [[frameNumber, contour, mask]
                       for contour, mask in zip(contours, masks)]
                pool.map(self.getLayers, tmp)
                #for x in tmp:
                    #self.getLayers(x)

        self.joinLayers()
        return self.layers

    def getLayers(self, data):
        frameNumber = data[0]
        bounds = data[1]
        mask = data[2]
        (x, y, w, h) = bounds
        tol = self.tolerance

        foundLayerIDs = set()
        for i, layer in enumerate(self.layers):
            if frameNumber - layer.lastFrame > self.ttolerance:
                continue

            lastXframes = min(40, len(layer))
            lastBounds = [bound for bounds in layer.bounds[-lastXframes:]
                          for bound in bounds]

            for j, bounds in enumerate(sorted(lastBounds, reverse=True)):
                if bounds is None:
                    break
                (x2, y2, w2, h2) = bounds
                if self.contoursOverlay((x-tol, y+h+tol), (x+w+tol, y-tol), (x2, y2+h2), (x2+w2, y2)):
                    layer.add(frameNumber, (x, y, w, h), mask)
                    foundLayerIDs.add(i)
                    break

        foundLayerIDs = sorted(list(foundLayerIDs))
        if len(foundLayerIDs) == 0:
            self.layers.append(
                Layer(frameNumber, (x, y, w, h), mask, self.config))
        if len(foundLayerIDs) > 1:
            self.mergeLayers(foundLayerIDs)

    def mergeLayers(self, foundLayerIDs):
        layers = self.getLayersByID(foundLayerIDs)
        layer1 = layers[0]
        for layer in layers[1:]:
            for i, (contours, masks) in enumerate(zip(layer.bounds, layer.masks)):
                for contour, mask in zip(contours, masks):
                    layer1.add(layer.startFrame + i, contour, mask)

        for i, id in enumerate(foundLayerIDs):
            del self.layers[id - i]

        self.layers.append(layer1)

    def joinLayers(self):
        self.layers.sort(key=lambda c: c.startFrame)
        minFrame = self.getMinStart(self.layers)
        maxFrame = self.getMaxEnd(self.layers)

        for i in range(minFrame, maxFrame):
            pL, indexes = self.getPossibleLayers(i)
            if len(pL) <= 1:
                continue
            merge = set()
            innerMax = self.getMaxEnd(pL)
            for x in range(self.getMinStart(pL), innerMax):
                for lc, l in enumerate(pL):
                    if l.startFrame < x or l.lastFrame > x:
                        continue
                    for lc2, l2 in enumerate(pL):
                        if lc2 == lc:
                            continue
                        for cnt in l.bounds[x-l.startFrame]:
                            for cnt2 in l2.bounds[x-l2.startFrame]:
                                if self.contoursOverlay(cnt, cnt2):
                                    merge.add(indexes[lc])
                                    merge.add(indexes[lc2])
            merge = list(merge)
            if len(merge) > 1:
                self.mergeLayers(megre)
            i = innerMax

    def getPossibleLayers(self, t):
        ret = []
        ii = []
        for i, layer in enumerate(self.layers):
            if layer.startFrame <= t and layer.lastFrame <= t:
                ret.append(layer)
                ii.append(i)
        return (ret, ii)

    def getMinStart(self, layers):
        minFrame = layers[0].startFrame
        for l in layers:
            if l.startFrame < minFrame:
                minFrame = l.startFrame
        return minFrame

    def getMaxEnd(self, layers):
        maxFrame = layers[0].lastFrame
        for l in layers:
            if l.lastFrame < maxFrame:
                maxFrame = l.lastFrame

        return maxFrame

    def contoursOverlay(self, l1, r1, l2, r2):
        # If one rectangle is on left side of other
        if(l1[0] >= r2[0] or l2[0] >= r1[0]):
            return False
        # If one rectangle is above other
        if(l1[1] <= r2[1] or l2[1] <= r1[1]):
            return False
        return True

    def getLayersByID(self, foundLayerIDs):
        layers = []
        for layerID in foundLayerIDs:
            layers.append(self.layers[layerID])

        layers.sort(key=lambda c: c.startFrame)
        return layers
