import imageio
import imutils
import numpy as np
from Layer import Layer 
import cv2
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

    def exportLayers(self, layers, outputPath):
        fps = self.fps
        writer = imageio.get_writer(outputPath, fps=fps)
        i=0
        for layer in layers:
            data = layer.data
            if len(data) < 10:
                continue
            for frame in data:
                (x, y, w, h) = frame[1]
                frame = frame[0]
                frame1 = np.zeros(shape=[1080, 1920, 3], dtype=np.uint8)
                frame1 = imutils.resize(frame1, width=512)
                frame1[y:y+frame.shape[0], x:x+frame.shape[1]] = frame
                cv2.putText(frame1,  str(i), (30,30), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255), 2)
                writer.append_data(np.array(frame1))
                #cv2.imshow("changes overlayed", frame)
                #cv2.waitKey(10) & 0XFF
            i += 1
        
        writer.close() 
        #cv2.destroyAllWindows()
    
    def exportOverlayed(self, layers, outputPath):
        fps = self.fps
        writer = imageio.get_writer(outputPath, fps=fps)
        
        maxLength = self.getMaxLengthOfLayers(layers)

        for i in range(maxLength):
            frame1 = np.zeros(shape=[1080, 1920, 3], dtype=np.uint8)
            frame1 = imutils.resize(frame1, width=512)

            for layer in layers:
                data = layer.data
                if len(layer.data) > i:
                    frame = layer.data[i]
                    (x, y, w, h) = frame[1]
                    frame = frame[0]

                    frame1[y:y+h, x:x+w] = frame
            writer.append_data(np.array(frame1))
        writer.close() 

    def getMaxLengthOfLayers(self, layers):
        maxLength = 0
        for layer in layers:
            if layer.getLength() > maxLength:
                maxLength = layer.getLength()
        return maxLength

