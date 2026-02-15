"""Heatmap generation for video activity visualization."""

from typing import List, Tuple

import numpy as np
from matplotlib import pyplot as plt


class HeatMap:
    """
    Generate heatmap visualization of video activity.

    Creates a heatmap showing areas of movement/activity in a video by
    accumulating contour locations over time.
    """

    def __init__(self, x: int, y: int, contours: List[List[Tuple[int, int, int, int]]], resize_factor: float = 1):
        """
        Initialize HeatMap.

        Args:
            x: Width of the heatmap image
            y: Height of the heatmap image
            contours: List of contour lists, where each contour is (x, y, w, h)
            resize_factor: Factor to scale contours (for upscaling from processed size)
        """
        self.image_bw = np.zeros(shape=[y, x, 3], dtype=np.float64)
        self._resize_factor = resize_factor
        self._create_image(contours)

    def _create_image(self, contours: List[List[Tuple[int, int, int, int]]]):
        """
        Create heatmap image from contours.

        Args:
            contours: List of contour lists to accumulate into heatmap
        """
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
        """Display the heatmap using matplotlib."""
        plt.imshow(self.image_bw * 255)
        plt.show()

    def save_image(self, path: str):
        """
        Save heatmap to file.

        Args:
            path: Output file path for the heatmap image
        """
        plt.imsave(path, (255 * self.image_bw).astype(np.uint8))
