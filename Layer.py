class Layer:
    #data = [(contour, (x,y,w,h)),]
    data = []
    startFrame = 0
    lastFrame = 0
    backgroundImage = []

    def __init__(self, startFrame, data, backgroundImage):
        self.startFrame = startFrame
        self.data.append(data)
        self.backgroundImage = backgroundImage

        print("Layer constructed")

    def add(self, frameNumber, data):
        self.lastFrame = frameNumber
        self.data.append(data)
