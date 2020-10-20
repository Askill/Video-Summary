from Application.Layer import Layer
from Application.Config import Config
from Application.VideoReader import VideoReader
from Application.Exporter import Exporter
from multiprocessing.pool import ThreadPool
import cv2
import numpy as np

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
        print("LayerFactory constructed")
        self.data = data
        if data is not None:
            self.extractLayers(data)

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
        self.removeStaticLayers()
    
    def freeMax(self):
        layers = []
        for l in self.layers:
            if l.getLength() < self.maxLayerLength:
                layers.append(l) 
        self.layers = layers
        self.removeStaticLayers()


    def extractLayers(self, data = None):
        

        if self.data is None:
            if data is None:
                print("LayerFactory data was none")
                return None
            else:
                self.data = data

        frameNumber = min(data)
        contours = data[frameNumber]
        for contour in contours:
            self.layers.append(Layer(frameNumber, contour, self.config))
  
        self.oldLayerIDs = []
        
        with ThreadPool(16) as pool:
            for frameNumber in sorted(data.keys()):
                contours = data[frameNumber]
                if frameNumber%5000 == 0:
                    print(f"{int(round(frameNumber/max(data.keys()), 2)*100)}% done with Layer extraction")

                tmp = [[frameNumber, contour] for contour in contours]
                #pool.map_async(self.getLayers, tmp)
                for x in tmp:
                    self.getLayers(x)

        self.freeMin()
        self.sortLayers()            
        self.cleanLayers()
        self.freeMax()
        
        
        return self.layers

    def getLayers(self, data):
        frameNumber = data[0]
        bounds = data[1]
        (x,y,w,h) = bounds
        tol = self.tolerance
        foundLayer = 0

        for i in range(0, len(self.layers)):
            if i in self.oldLayerIDs:
                continue
            if frameNumber - self.layers[i].lastFrame > self.ttolerance:
                self.oldLayerIDs.append(i)
                continue

            for bounds in self.layers[i].bounds[-1]:
                if bounds is None or foundLayer >= self.config["LayersPerContour"]:
                    break
                (x2,y2,w2,h2) = bounds
                if self.contoursOverlay((x-tol,y+h+tol), (x+w+tol,y-tol), (x2,y2+h2), (x2+w2,y2)):
                    self.layers[i].add(frameNumber, (x,y,w,h))
                    foundLayer += 1
                    #break

        if foundLayer == 0:
            self.layers.append(Layer(frameNumber, (x,y,w,h), self.config))

    def contoursOverlay(self, l1, r1, l2, r2): 
        # If one rectangle is on left side of other 
        if(l1[0] >= r2[0] or l2[0] >= r1[0]): 
            return False
        # If one rectangle is above other 
        if(l1[1] <= r2[1] or l2[1] <= r1[1]): 
            return False
        return True

    def fillLayers(self):

        listOfFrames = Exporter(self.config).makeListOfFrames(self.layers)
        videoReader = VideoReader(self.config, listOfFrames)
        videoReader.fillBuffer()

        while not videoReader.videoEnded():
            frameCount, frame = videoReader.pop()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            for i, layer in enumerate(self.layers):
                if i % 20 == 0:
                    print(f"filled {int(round(i/len(self.layers),2)*100)}% of all Layers")
                
                if layer.startFrame <= frameCount and layer.startFrame + len(layer.bounds) > frameCount:
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

        videoReader.thread.join()

    def sortLayers(self):
        self.layers.sort(key = lambda c:c.startFrame)

    def cleanLayers(self):
        for layer in self.layers:
            layer.clusterDelete()
