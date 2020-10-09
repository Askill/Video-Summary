import imageio
import imutils
import numpy as np
from Layer import Layer
import cv2
from VideoReader import VideoReader


class Exporter:
    fps = 30

    def __init__(self):
        print("Exporter initiated")

    def export(self, frames, outputPath):
        fps = self.fps
        writer = imageio.get_writer(outputPath, fps=fps)
        for frame in frames:
            writer.append_data(np.array(frame))
        writer.close()

    def exportLayers(self,  layers, outputPath, resizeWidth):
        underlay = cv2.VideoCapture(footagePath).read()[1]
        fps = self.fps
        writer = imageio.get_writer(outputPath, fps=fps)
        i = 0
        for layer in layers:
            data = layer.data
            contours = layer.bounds
            if len(data) < 10:
                continue
            for frame, contour in zip(data, contours):
                (x, y, w, h) = contour
                frame = frame
                frame1 = underlay
                frame1 = imutils.resize(frame1, width=resizeWidth)
                frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                frame1[y:y+frame.shape[0], x:x+frame.shape[1]] = frame
                cv2.putText(frame1,  str(i), (30, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                writer.append_data(np.array(frame1))
                #cv2.imshow("changes overlayed", frame)
                #cv2.waitKey(10) & 0XFF
            i += 1

        writer.close()
        # cv2.destroyAllWindows()

    def exportOverlayed(self, layers, footagePath, outputPath, resizeWidth):


        listOfFrames = self.makeListOfFrames(layers)
        videoReader = VideoReader(footagePath, listOfFrames)
        videoReader.fillBuffer()
        maxLength = self.getMaxLengthOfLayers(layers)
        underlay = cv2.VideoCapture(footagePath).read()[1]
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
                    (x, y, w, h) = layer.bounds[frameCount - layer.startFrame]
                    factor = videoReader.w / resizeWidth
                    x = int(x * factor)
                    y = int(y * factor)
                    w = int(w * factor)
                    h = int(h * factor)
                    # if exportFrame as index instead of frameCount - layer.startFrame  then we have layer after layer
                    frame2 = frames[frameCount - layer.startFrame]
                    frame2[y:y+h, x:x+w] = frame[y:y+h, x:x+w]
                    frames[frameCount - layer.startFrame] = np.copy(frame2)


        videoReader.thread.join()


        fps = self.fps
        writer = imageio.get_writer(outputPath, fps=fps)
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
