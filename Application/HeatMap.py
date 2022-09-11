import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

class HeatMap:
    def __init__(self, x, y, contours, resize_factor=1):
        self.image_bw = np.zeros(shape=[y, x, 3], dtype=np.float64)
        self._resize_factor = resize_factor
        self._create_image(contours)

    def _create_image(self, contours):
        for contour in contours:
            for x, y, w, h in contour:
                x, y, w, h = (
                    x * self._resize_factor,
                    y * self._resize_factor,
                    w * self._resize_factor,
                    h * self._resize_factor,
                )
                self.image_bw[int(y) : int(y + h), int(x) : int(x + w)] += 1

        self.image_bw = np.nan_to_num(self.image_bw / self.image_bw.sum(axis=1)[:, np.newaxis], 0)

    def show_image(self):
        plt.imshow(self.image_bw * 255)
        plt.show()

    def save__image(self, path):
        im = Image.fromarray(self.image_bw * 255)
        im.save(path)