import math
from PIL import Image, ImageDraw
import random
import imageio
import glob
import os
import numpy as np


fps = 30
xmax = 1920
ymax = 1080

length = 1  # in minutes
numberOfEvents = 4

dirname = os.path.dirname(__file__)
outputPath = os.path.join(dirname, "out.mp4")


def getRandomColorString():
    return "#{:06x}".format(random.randint(0, 256 ** 3))


def genVideo():
    writer = imageio.get_writer(outputPath, fps=fps)
    writer.append_data(np.zeros(shape=[1080, 1920, 3], dtype=np.uint8))
    writer.append_data(np.zeros(shape=[1080, 1920, 3], dtype=np.uint8))

    for i in range(numberOfEvents):
        objectWidth = (5 + random.randint(0, 5)) * xmax / 100
        objectHeight = (10 + random.randint(-5, 5)) * ymax / 100

        objectX = random.randint(0, xmax)
        objectY = random.randint(0, ymax)

        objectSpeedX = random.randint(1, 5)
        objectSpeedY = random.randint(1, 5)
        color = getRandomColorString()

        for j in range(int(fps * length * 60 / numberOfEvents)):
            objectX -= objectSpeedX
            objectY -= objectSpeedY

            objectShape = [(objectX, objectY), (objectX + objectWidth, objectY + objectHeight)]
            img = Image.new("RGB", (xmax, ymax))
            img1 = ImageDraw.Draw(img)
            img1.rectangle(objectShape, fill=color)
            writer.append_data(np.array(img))

    writer.close()


genVideo()
