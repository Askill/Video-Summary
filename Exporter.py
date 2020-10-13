import imageio
import imutils
import numpy as np
from Layer import Layer
import cv2
from VideoReader import VideoReader


class Exporter:
    fps = 30

    def __init__(self, config):
        self.footagePath = config["inputPath"]
        self.outputPath = config["outputPath"]
        self.resizeWidth = config["resizeWidth"]
        self.config = config
        print("Exporter initiated")

    def export(self):
        fps = self.fps
        writer = imageio.get_writer(outputPath, fps=fps)
        for frame in frames:
            writer.append_data(np.array(frame))
        writer.close()

    def exportLayers(self,  layers):

        listOfFrames = self.makeListOfFrames(layers)
        videoReader = VideoReader(self.config, listOfFrames)
        videoReader.fillBuffer()
        maxLength = self.getMaxLengthOfLayers(layers)
        underlay = cv2.VideoCapture(self.footagePath).read()[1]
        underlay = cv2.cvtColor(underlay, cv2.COLOR_BGR2RGB)
        frames = [underlay]*maxLength
        exportFrame = 0

        self.fps = videoReader.getFPS()
        writer = imageio.get_writer(self.outputPath, fps=self.fps)
        while not videoReader.videoEnded():
            frameCount, frame = videoReader.pop()
            if frameCount % (60*self.fps) == 0:
                print("Minutes processed: ", frameCount/(60*self.fps))
            if frame is None:
                print("ContourExtractor: frame was None")
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            frame2 = underlay
            for layer in layers:
                if layer.startFrame <= frameCount and layer.startFrame + len(layer.bounds) > frameCount:
                    for (x, y, w, h) in layer.bounds[frameCount - layer.startFrame]:
                        factor = videoReader.w / self.resizeWidth
                        x = int(x * factor)
                        y = int(y * factor)
                        w = int(w * factor)
                        h = int(h * factor)
                        
                        frame2[y:y+h, x:x+w] = frame[y:y+h, x:x+w]
            writer.append_data(frame2)


        videoReader.thread.join()


    def exportOverlayed(self, layers):

        listOfFrames = self.makeListOfFrames(layers)
        videoReader = VideoReader(self.config, listOfFrames)
        videoReader.fillBuffer()
        maxLength = self.getMaxLengthOfLayers(layers)
        underlay = cv2.VideoCapture(self.footagePath).read()[1]
        underlay = cv2.cvtColor(underlay, cv2.COLOR_BGR2RGB)
        frames = [underlay]*maxLength
        exportFrame = 0

        
        while not videoReader.videoEnded():
            frameCount, frame = videoReader.pop()
            if frameCount % (60*self.fps) == 0:
                print("Minutes processed: ", frameCount/(60*self.fps))
            if frame is None:
                print("ContourExtractor: frame was None")
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            for layer in layers:
                if layer.startFrame <= frameCount and layer.startFrame + len(layer.bounds) > frameCount:
                    for (x, y, w, h) in layer.bounds[frameCount - layer.startFrame]:
                        factor = videoReader.w / self.resizeWidth
                        x = int(x * factor)
                        y = int(y * factor)
                        w = int(w * factor)
                        h = int(h * factor)
                        # if exportFrame as index instead of frameCount - layer.startFrame  then we have layer after layer
                        frame2 = frames[frameCount - layer.startFrame]
                        frame2[y:y+h, x:x+w] = frame[y:y+h, x:x+w]
                        frames[frameCount - layer.startFrame] = np.copy(frame2)
        videoReader.thread.join()

        self.fps = videoReader.getFPS()
        fps = self.fps
        writer = imageio.get_writer(self.outputPath, fps=fps)
        for frame in frames:
            writer.append_data(frame)

        writer.close()

    def getMaxLengthOfLayers(self, layers):
        maxLength = 0
        for layer in layers:
            if layer.getLength() > maxLength:
                maxLength = layer.getLength()
        return maxLength

    def makeListOfFrames(self, layers):
        '''Returns set of all Frames which are relavant to the Layers'''
        frameNumbers = set()
        for layer in layers:
            frameNumbers.update(
                list(range(layer.startFrame, layer.startFrame + len(layer.bounds))))

        return list(frameNumbers)
