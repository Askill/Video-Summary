from Layer import Layer

class LayerFactory:
    data = {}
    layers = []
    tolerance = 5
    def __init__(self, data=None):
        print("LayerFactory constructed")
        self.data = data
        if data is not None:
            self.extractLayers(data)

    def freeData(self, maxLayerLength):
        self.data.clear()
        for i in range(len(self.layers)):
            if self.layers[i].getLength() > maxLayerLength:
                del self.layers[i] 


    def extractLayers(self, data = None):
        tol = self.tolerance

        if self.data is None:
            if data is None:
                print("LayerFactory data was none")
                return None
            else:
                self.data = data

        layers = []
        frameNumber = min(data)
        contours = data[frameNumber]

        for contour in contours:
            layers.append(Layer(frameNumber, contour))

        # inserts all the fucking contours as layers?
        for frameNumber in sorted(data):
            contours = data[frameNumber]
            for (x,y,w,h) in contours:
                foundLayer = False
                i = 0
                for i in range(0, len(layers)):
                    layer = layers[i]

                    if len(layer.bounds[-1]) != 4:
                        # should never be called, hints at problem in ContourExtractor
                        print("LayerFactory: Layer knew no bounds")
                        continue

                    if frameNumber - layer.lastFrame <= 5:
                        (x2,y2,w2,h2) = layer.bounds[-1]
                        if self.contoursOverlay((x-tol,y+h+tol), (x+w+tol,y-tol), (x2,y2+h2), (x2+w2,y2)):
                            foundLayer = True
                            layer.add(frameNumber, (x,y,w,h))
                            break
                            
                    layers[i] = layer
                if not foundLayer:
                    layers.append(Layer(frameNumber, (x,y,w,h)))

        self.layers = layers


    def contoursOverlay(self, l1, r1, l2, r2): 
      
        # If one rectangle is on left side of other 
        if(l1[0] >= r2[0] or l2[0] >= r1[0]): 
            return False
    
        # If one rectangle is above other 
        if(l1[1] <= r2[1] or l2[1] <= r1[1]): 
            return False
    
        return True

    def fillLayers(self, footagePath):
        for i in range(len(self.layers)):
            self.layers[i].fill(footagePath)

    def sortLayers(self):
        # straight bubble
        self.layers.sort(key = lambda c:c.lastFrame)




                
            
        
