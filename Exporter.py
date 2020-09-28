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
        for layer in layers:
            data = layer.data
            for frame in data:
                (x, y, w, h) = frame[1]
                frame = frame[0]
                frame1 = np.zeros(shape=[1080, 1920, 3], dtype=np.uint8)
                frame1 = imutils.resize(frame1, width=512)
                frame1[y:y+frame.shape[0], x:x+frame.shape[1]] = frame
                writer.append_data(np.array(frame1))
                #cv2.imshow("changes overlayed", frame)
                #cv2.waitKey(10) & 0XFF
        
        writer.close() 
        #cv2.destroyAllWindows()
