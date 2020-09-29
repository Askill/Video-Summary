class Layer:
    #data = [(contour, (x,y,w,h)),]

    startFrame = None
    lastFrame = None

    def __init__(self, startFrame, data):
        self.startFrame = startFrame
        self.lastFrame = startFrame
        self.data = []
        self.data.append(data)

        print("Layer constructed")

    def add(self, frameNumber, data):
        if not (self.startFrame + len(self.data) - frameNumber < 0):
            self.lastFrame = frameNumber
            self.data.append(data)
