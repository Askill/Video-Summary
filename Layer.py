class Layer:
    #data = [(contour, (x,y,w,h)),]
    data = []
    startFrame = None
    lastFrame = None
    backgroundImage = []

    def __init__(self, startFrame, data):
        self.startFrame = startFrame
        self.lastFrame = startFrame
        self.data.append(data)

        print("Layer constructed")

    def add(self, frameNumber, data):
        self.lastFrame = frameNumber
        self.data.append(data)
