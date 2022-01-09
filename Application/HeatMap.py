import numpy as np
from matplotlib import pyplot as plt

class HeatMap:
    def __init__(self, x, y, contours, resizeFactor = 1):
        self.imageBW = np.zeros(shape=[y, x, 3], dtype=np.float64)
        self._resizeFactor = resizeFactor
        self._createImage(contours)

    def _createImage(self, contours):
        for contour in contours:
            for x, y, w, h in contour:
                x, y, w, h = x*self._resizeFactor, y*self._resizeFactor, w*self._resizeFactor, h*self._resizeFactor
                self.imageBW[int(y):int(y+h), int(x):int(x+w)] += 1

        self.imageBW = np.nan_to_num(self.imageBW/ self.imageBW.sum(axis=1)[:, np.newaxis], 0)

    def showImage(self):
        plt.imshow(self.imageBW*255)
        plt.show()
