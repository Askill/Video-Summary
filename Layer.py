class Layer:
    #data = [(contour, (x,y,w,h)),]
    data = []
    startFrame = 0
    backgroundImage = []
    def __init__(self, startFrame, data, backgroundImage):
        self.startFrame = startFrame
        self.data = data
        self.backgroundImage = backgroundImage
        
        print("Layer constructed")