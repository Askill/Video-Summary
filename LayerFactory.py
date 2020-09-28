from Layer import Layer

class LayerFactory:
    data = {}
    layers = []
    def __init__(self, data=None):
        print("LayerFactory constructed")
        self.data = data
        if data is not None:
            self.extractLayers(data)

    def extractLayers(self, data = None):
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
        for frameNumber, contours in data.items():
            for contour, (x,y,w,h) in contours:
                for layer in layers:
                    if frameNumber - layer.lastFrame <= 5:
                        if len(layer.data[-1][1]) != 4:
                            print("LayerFactory: Layer knew no bounds")
                            continue

                        (x2,y2,w2,h2) = layer.data[-1][1]
                        tol = 10
                        if self.contoursOverlay((x-tol,y+h+tol), (x+w+tol,y-tol), (x2,y2+h2), (x2+w2,y2)):
                            layer.add(frameNumber, (contour, (x,y,w,h)))
                            break

                    layers.append(Layer(frameNumber, (contour, (x,y,w,h))))

        self.layers = layers


    def contoursOverlay(self, l1, r1, l2, r2): 
      
        # If one rectangle is on left side of other 
        if(l1[0] >= r2[0] or l2[0] >= r1[0]): 
            return False
    
        # If one rectangle is above other 
        if(l1[1] <= r2[1] or l2[1] <= r1[1]): 
            return False
    
        return True



                
            
        
