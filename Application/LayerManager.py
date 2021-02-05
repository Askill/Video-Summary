from Application.Layer import Layer
from Application.Config import Config
from Application.VideoReader import VideoReader
from Application.Exporter import Exporter
from multiprocessing.pool import ThreadPool
from Application.Classifiers.Classifier import Classifier
import cv2
import numpy as np
import time

class LayerManager:
    def __init__(self, config, layers):
        self.data = {}
        self.layers = layers
        self.tolerance = config["tolerance"]
        self.ttolerance = config["ttolerance"]
        self.minLayerLength = config["minLayerLength"]
        self.maxLayerLength = config["maxLayerLength"]
        self.resizeWidth = config["resizeWidth"]
        self.footagePath = config["inputPath"]
        self.config = config
        #self.classifier = Classifier()
        self.tags = []
        print("LayerManager constructed")

    def transformLayers(self):
        print("'Cleaning' Layers")
        print("Before deleting short layers ", len(self.layers))
        self.freeMin()
        print("Before deleting long layers ", len(self.layers))
        self.freeMax()
        self.sortLayers()     
        self.calcStats()
        print("Before deleting sparse layers ", len(self.layers))
        self.deleteSparse()
        print("after deleting sparse layers ", len(self.layers))

    def deleteSparse(self):
        toDelete = []
        for i, l in enumerate(self.layers):
            empty = l.bounds.count([])
            if empty / len(l) > 0.5:
                toDelete.append(i)

        for i, id in enumerate(toDelete):
            del self.layers[id - i]

    def calcStats(self):
        for layer in self.layers:
            layer.calcStats()

    def freeMin(self):
        self.data.clear()
        layers = []
        for l in self.layers:
            if len(l) > self.minLayerLength:
                layers.append(l) 
        self.layers = layers
        
    def freeMax(self):
        layers = []
        for l in self.layers:
            if len(l) < self.maxLayerLength:
                layers.append(l) 
        self.layers = layers

    def tagLayers(self):
        '''Use classifieres the tag all Layers, by reading the contour content from the original video, then applying the classifier'''
        print("Tagging Layers")
        exporter = Exporter(self.config)
        start = time.time()
        for i, layer in enumerate(self.layers):
            print(f"{round(i/len(self.layers)*100,2)} {round((time.time() - start), 2)}")
            start = time.time()
            if len(layer.bounds[0]) == 0:
                continue
            listOfFrames = exporter.makeListOfFrames([layer])

            videoReader = VideoReader(self.config, listOfFrames)
            videoReader.fillBuffer()

            while not videoReader.videoEnded():
                frameCount, frame = videoReader.pop()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                data = []
                for (x, y, w, h) in layer.bounds[frameCount - layer.startFrame]:
                    if x is None:
                        break
                    factor = videoReader.w / self.resizeWidth
                    x = int(x * factor)
                    y = int(y * factor)
                    w = int(w * factor)
                    h = int(h * factor)
                    data.append(np.copy(frame[y:y+h, x:x+w]))
                layer.data.append(data)
            tags = self.classifier.tagLayer(layer.data)
            print(tags)
            self.tags.append(tags)

            videoReader.thread.join()

    def sortLayers(self):
        self.layers.sort(key = lambda c:c.startFrame)
