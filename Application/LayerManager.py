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
        self.classifier = Classifier()
        self.tags = []
        print("LayerManager constructed")



    def cleanLayers(self):
        self.freeMin()
        self.sortLayers()            
        self.cleanLayers2()
        self.freeMax()

    def removeStaticLayers(self):
        '''Removes Layers with little to no movement'''
        layers = []
        for i, layer in enumerate(self.layers):
            checks = 0
            for bound in layer.bounds[0]:
                if bound[0] is None:
                    continue
                for bound2 in layer.bounds[-1]:
                    if bound2[0] is None:
                        continue
                    if abs(bound[0] - bound2[0]) < 10:
                        checks += 1
                    if abs(bound[1] - bound2[1]) < 10:
                        checks += 1
            if checks <= 2:
                layers.append(layer)
        self.layers = layers


    def freeMin(self):
        self.data.clear()
        layers = []
        for l in self.layers:
            if l.getLength() > self.minLayerLength:
                layers.append(l) 
        self.layers = layers
        
    
    def freeMax(self):
        layers = []
        for l in self.layers:
            if l.getLength() < self.maxLayerLength:
                layers.append(l) 
        self.layers = layers
        

    def tagLayers(self):
        '''Use classifieres the tag all Layers, by reading the contour content from the original video, then applying the classifier'''
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

    def cleanLayers2(self):
        for layer in self.layers:
            layer.clusterDelete()
