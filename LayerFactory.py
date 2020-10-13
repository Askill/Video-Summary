from Layer import Layer
from Config import Config

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
        print("LayerFactory constructed")
        self.data = data
        if data is not None:
            self.extractLayers(data)



    def removeStaticLayers(self):
        '''Removes Layers with little to no movement'''
        layers = []
        for i, layer in enumerate(self.layers):
            checks = 0
            if abs(self.layers[i].bounds[0][0][0] - self.layers[i].bounds[-1][0][0]) < 5:
                checks += 1
            if abs(self.layers[i].bounds[0][0][1] - self.layers[i].bounds[-1][0][1]) < 5:
                checks += 1
            if checks <= 2:
                layers.append(layer)
        self.layers = layers


    def freeData(self):
        self.data.clear()
        layers = []
        for l in self.layers:
            if l.getLength() < self.maxLayerLength and l.getLength() > self.minLayerLength:
                layers.append(l) 
        self.layers = layers
        self.removeStaticLayers()


    def extractLayers(self, data = None):
        tol = self.tolerance

        if self.data is None:
            if data is None:
                print("LayerFactory data was none")
                return None
            else:
                self.data = data

        frameNumber = min(data)
        contours = data[frameNumber]
        for contour in contours:
            self.layers.append(Layer(frameNumber, contour))
  
        oldLayerIDs = []
        # inserts all the fucking contours as layers?
        for frameNumber in sorted(data.keys()):
            contours = data[frameNumber]
            if frameNumber%5000 == 0:
                print(f"{int(round(frameNumber/max(data.keys()), 2)*100)}% done with Layer extraction")

            for (x,y,w,h) in contours:
                foundLayer = False
                for i in set(range(0, len(self.layers))).difference(set(oldLayerIDs)):
                    if frameNumber - self.layers[i].lastFrame > self.ttolerance:
                        oldLayerIDs.append(i)
                        continue

                    for bounds in self.layers[i].bounds[-1]:
                        if bounds is None:
                            break
                        (x2,y2,w2,h2) = bounds
                        if self.contoursOverlay((x-tol,y+h+tol), (x+w+tol,y-tol), (x2,y2+h2), (x2+w2,y2)):
                            self.layers[i].add(frameNumber, (x,y,w,h))
                            foundLayer = True
                            break

                if not foundLayer:
                    self.layers.append(Layer(frameNumber, (x,y,w,h)))
        self.freeData()
        self.sortLayers()
        return self.layers

    def contoursOverlay(self, l1, r1, l2, r2): 
        # If one rectangle is on left side of other 
        if(l1[0] >= r2[0] or l2[0] >= r1[0]): 
            return False
        # If one rectangle is above other 
        if(l1[1] <= r2[1] or l2[1] <= r1[1]): 
            return False
        return True

    def fillLayers(self):
        for i in range(len(self.layers)):
            if i % 20 == 0:
                print(f"filled {int(round(i/len(self.layers),2)*100)}% of all Layers")
            self.layers[i].fill(self.footagePath, self.resizeWidth)

    def sortLayers(self):
        self.layers.sort(key = lambda c:c.startFrame)
