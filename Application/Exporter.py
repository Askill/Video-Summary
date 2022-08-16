import pickle
import time
from datetime import datetime

import cv2
import imageio
import imutils
import numpy as np

from Application.VideoReader import VideoReader


class Exporter:
    fps = 30

    def __init__(self, config):
        self.footagePath = config["inputPath"]
        self.outputPath = config["outputPath"]
        self.resizeWidth = config["resizeWidth"]
        self.config = config
        print("Exporter initiated")

    def export(self, layers, contours, masks, raw=True, overlayed=True, blackBackground=False, showProgress=False):
        if raw:
            self.exportRawData(layers, contours, masks)
        if overlayed:
            self.exportOverlayed(layers, blackBackground, showProgress)
        else:
            self.exportLayers(layers)

    def exportLayers(self, layers):
        listOfFrames = self.makeListOfFrames(layers)
        with VideoReader(self.config, listOfFrames) as videoReader:
            
            underlay = cv2.VideoCapture(self.footagePath).read()[1]
            underlay = cv2.cvtColor(underlay, cv2.COLOR_BGR2RGB)

            fps = videoReader.getFPS()
            writer = imageio.get_writer(self.outputPath, fps=fps)

            start = time.time()
            for i, layer in enumerate(layers):
                print(f"\r {i}/{len(layers)} {round(i/len(layers)*100,2)}% {round((time.time() - start), 2)}s", end="\r")
                if len(layer.bounds[0]) == 0:
                    continue
                videoReader = VideoReader(self.config)
                listOfFrames = self.makeListOfFrames([layer])
                videoReader.fillBuffer(listOfFrames)
                while not videoReader.videoEnded():
                    frameCount, frame = videoReader.pop()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame2 = np.copy(underlay)
                    for (x, y, w, h) in layer.bounds[frameCount - layer.startFrame]:
                        if x is None:
                            continue
                        factor = videoReader.w / self.resizeWidth
                        x, y, w, h = (int(x * factor), int(y * factor), int(w * factor), int(h * factor))

                        frame2[y : y + h, x : x + w] = np.copy(frame[y : y + h, x : x + w])

                        self.addTimestamp(frame2, videoReader, frameCount, layer, x, y, w, h)
                    writer.append_data(frame2)

            writer.close()

    def exportOverlayed(self, layers, blackBackground=False, showProgress=False):

        listOfFrames = self.makeListOfFrames(layers)
        maxLength = self.getMaxLengthOfLayers(layers)

        if blackBackground:
            underlay = np.zeros(shape=[videoReader.h, videoReader.w, 3], dtype=np.uint8)
        else:
            underlay = cv2.VideoCapture(self.footagePath).read()[1]
            underlay = cv2.cvtColor(underlay, cv2.COLOR_BGR2RGB)

        frames = []
        for i in range(maxLength):
            frames.append(np.copy(underlay))

        with VideoReader(self.config, listOfFrames) as videoReader:
            while not videoReader.videoEnded():
                frameCount, frame = videoReader.pop()
                if frameCount % (60 * self.fps) == 0:
                    print("Minutes processed: ", frameCount / (60 * self.fps), end="\r")
                if frame is None:
                    print("ContourExtractor: frame was None")
                    continue

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                for layer in layers:
                    if layer.startFrame <= frameCount and layer.startFrame + len(layer.bounds) > frameCount:
                        for i in range(0, len(layer.bounds[frameCount - layer.startFrame])):
                            try:
                                x, y, w, h = layer.bounds[frameCount - layer.startFrame][i]
                                if None in (x, y, w, h):
                                    break
                                factor = videoReader.w / self.resizeWidth
                                x, y, w, h = (int(x * factor), int(y * factor), int(w * factor), int(h * factor))

                                mask = self.getMask(i, frameCount, layer, w, h)
                                background = frames[frameCount - layer.startFrame + layer.exportOffset]
                                self.addMaskedContent(frame, x, y, w, h, mask, background)
                                frames[frameCount - layer.startFrame + layer.exportOffset] = np.copy(background)

                                if showProgress:
                                    cv2.imshow("changes x", background)
                                    cv2.waitKey(10) & 0xFF

                                self.addTimestamp(frames[frameCount - layer.startFrame + layer.exportOffset], videoReader, frameCount, layer, x, y, w, h)
                            except:
                                continue

        writer = imageio.get_writer(self.outputPath, fps=videoReader.getFPS())
        for frame in frames:
            writer.append_data(frame)

        writer.close()

    def addMaskedContent(self, frame, x, y, w, h, mask, background):
        maskedFrame = np.copy(
            cv2.bitwise_and(
                background[y : y + h, x : x + w],
                background[y : y + h, x : x + w],
                mask=cv2.bitwise_not(mask),
            )
        )
        background[y : y + h, x : x + w] = cv2.addWeighted(
            maskedFrame,
            1,
            np.copy(cv2.bitwise_and(frame[y : y + h, x : x + w], frame[y : y + h, x : x + w], mask=mask)),
            1,
            0,
        )

    def addTimestamp(self, frame, videoReader, frameCount, layer, x, y, w, h):
        time = datetime.fromtimestamp(int(frameCount / self.fps) + videoReader.getStartTime())
        cv2.putText(
            frame,
            f"{time.hour}:{time.minute}:{time.second}",
            (int(x + w / 2), int(y + h / 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

    def getMask(self, i, frameCount, layer, w, h):
        mask = layer.masks[frameCount - layer.startFrame][i]
        mask = imutils.resize(mask, width=w, height=h + 1)
        mask = np.resize(mask, (h, w))
        mask = cv2.erode(mask, None, iterations=10)
        mask *= 255
        return mask

    def exportRawData(self, layers, contours, masks):
        with open(self.config["importPath"], "wb+") as file:
            pickle.dump((layers, contours, masks), file)

    def getMaxLengthOfLayers(self, layers):
        maxLength = 0
        for layer in layers:
            if layer.getLength() > maxLength:
                maxLength = layer.getLength()
        return maxLength

    def makeListOfFrames(self, layers):
        """Returns set of all Frames which are relavant to the Layers"""
        frameNumbers = set()
        for layer in layers:
            frameNumbers.update(list(range(layer.startFrame, layer.startFrame + len(layer))))

        return sorted(list(frameNumbers))
