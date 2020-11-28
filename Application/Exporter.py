import imageio
import imutils
import numpy as np
from Application.Layer import Layer
import cv2
from Application.VideoReader import VideoReader
import pickle
import time 

class Exporter:
    fps = 30

    def __init__(self, config):
        self.footagePath = config["inputPath"]
        self.outputPath = config["outputPath"]
        self.resizeWidth = config["resizeWidth"]
        self.config = config
        print("Exporter initiated")

    def export(self, layers, contours, masks, raw = True, overlayed = True):
        if raw:
            self.exportRawData(layers, contours, masks)
        if overlayed:
            self.exportOverlayed(layers)
        else:
            self.exportLayers(layers)
    

    def exportLayers(self, layers):

        listOfFrames = self.makeListOfFrames(layers)
        videoReader = VideoReader(self.config, listOfFrames)
        videoReader.fillBuffer()
        maxLength = self.getMaxLengthOfLayers(layers)
        underlay = cv2.VideoCapture(self.footagePath).read()[1]
        underlay = cv2.cvtColor(underlay, cv2.COLOR_BGR2RGB)
        exportFrame = 0

        self.fps = videoReader.getFPS()
        writer = imageio.get_writer(self.outputPath, fps=self.fps)

        start = time.time()
        for i, layer in enumerate(layers):
            print(f"\r {i}/{len(layers)} {round(i/len(layers)*100,2)}% {round((time.time() - start), 2)}s", end='\r')
            
            if len(layer.bounds[0]) == 0:
                continue
            if layer.stats["dev"] < 5:
                continue
            
            listOfFrames = self.makeListOfFrames([layer])

            videoReader = VideoReader(self.config, listOfFrames)
            videoReader.fillBuffer()

            while not videoReader.videoEnded():
                frameCount, frame = videoReader.pop()

                if frameCount % (60*self.fps) == 0:
                    print("Minutes processed: ", frameCount/(60*self.fps))

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
                frame2 = np.copy(underlay)
                for (x, y, w, h) in layer.bounds[frameCount - layer.startFrame]:
                    if x is None:
                        continue
                    factor = videoReader.w / self.resizeWidth
                    x = int(x * factor)
                    y = int(y * factor)
                    w = int(w * factor)
                    h = int(h * factor)
                    
                    frame2[y:y+h, x:x+w] = np.copy(frame[y:y+h, x:x+w])

                    cv2.putText(frame2, str(i) + "  " + str(int(frameCount/self.fps)), (int(x+w/2), int(y+h/2)), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255), 2)
                cv2.putText(frame2, str(layer.stats["avg"]) + "  " + str(layer.stats["var"]) + "  " + str(layer.stats["dev"]), (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,255), 2)
                writer.append_data(frame2)

            videoReader.thread.join()
            videoReader.vc.release()
        writer.close()
        

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
                print("Minutes processed: ", frameCount/(60*self.fps), end="\r")
            if frame is None:
                print("ContourExtractor: frame was None")
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            for layer in layers:
                if layer.startFrame <= frameCount and layer.startFrame + len(layer.bounds) > frameCount:
                    for i in range(0, len(layer.bounds[frameCount - layer.startFrame])):
                        (x, y, w, h) = layer.bounds[frameCount - layer.startFrame][i]
                        mask = layer.masks[frameCount - layer.startFrame][i]
                        
                        if x is None:
                            break
                        factor = videoReader.w / self.resizeWidth
                        x = int(x * factor)
                        y = int(y * factor)
                        w = int(w * factor)
                        h = int(h * factor)
                        mask = imutils.resize(mask, width=w, height=h+1)
                        mask = np.resize(mask, (h,w))
                        
                        frame2 = frames[frameCount - layer.startFrame]
                        #frame2[y:y+h, x:x+w] =  cv2.bitwise_or(frame2[y:y+h, x:x+w], frame2[y:y+h, x:x+w], mask=cv2.bitwise_not(mask)))
                        #frame2[y:y+h, x:x+w] = np.zeros((h, w, 3))
                        frame2[y:y+h, x:x+w] = np.copy(cv2.bitwise_and(underlay[y:y+h, x:x+w], underlay[y:y+h, x:x+w], mask=cv2.bitwise_not(mask)))
                        frame2[y:y+h, x:x+w] = cv2.addWeighted(np.copy(frame2[y:y+h, x:x+w]),1, np.copy(cv2.bitwise_and(frame[y:y+h, x:x+w], frame[y:y+h, x:x+w], mask=mask)),.5,0)
                        
                        frames[frameCount - layer.startFrame] = np.copy(frame2) 
                        cv2.imshow("changes x", frame2)
                        cv2.waitKey(10) & 0XFF
                        cv2.putText(frames[frameCount - layer.startFrame],  str(int(frameCount/self.fps)), (int(x+w/2), int(y+h/2)), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255), 2)

        videoReader.thread.join()
        videoReader.vc.release()

        self.fps = videoReader.getFPS()
        fps = self.fps
        writer = imageio.get_writer(self.outputPath, fps=fps)
        for frame in frames:
            writer.append_data(frame)

        writer.close()

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
        '''Returns set of all Frames which are relavant to the Layers'''
        frameNumbers = set()
        for layer in layers:
            frameNumbers.update(
                list(range(layer.startFrame, layer.startFrame + len(layer.bounds))))

        return sorted(list(frameNumbers))
