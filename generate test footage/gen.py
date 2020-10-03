
import math 
from PIL import Image, ImageDraw 
import random
import imageio
import glob
import os
import numpy as np

def getRandomColorString():
    return '#{:06x}'.format(random.randint(0, 256**3))

fps = 30
xmax = 1920
ymax = 1080
# in minutes
length = 1
numberOfEvents = 4
dirname = os.path.dirname(__file__)

imageType = ".png"

imagesPath = os.path.join(dirname, 'images')+"/"
outputPath = os.path.join(dirname, 'out.mp4')

def genImages():
    counter = 0
    writer = imageio.get_writer(outputPath, fps=fps)
    writer.append_data(np.zeros(shape=[1080, 1920, 3], dtype=np.uint8))
    writer.append_data(np.zeros(shape=[1080, 1920, 3], dtype=np.uint8))
    for i in range(numberOfEvents):

        objectWidth = (5 + random.randint(0, 5)) * xmax / 100 
        objectHeight = (10 + random.randint(-5, 5)) * ymax / 100

        objectX = random.randint(0, xmax)
        objectY = random.randint(0, ymax)

        objectSpeedX = random.randint( 1 ,5 )
        objectSpeedY = random.randint( 1, 5 )
        color = getRandomColorString()

        for j in range(int(fps*length*60 / numberOfEvents)):
            counter+=1
            objectX -= objectSpeedX
            objectY -= objectSpeedY

            objectShape = [(objectX, objectY), (objectX + objectWidth, objectY + objectHeight)] 
            
            
            img = Image.new("RGB", (xmax, ymax)) 
            # create rectangle image 
            img1 = ImageDraw.Draw(img)   
            
            img1.rectangle(objectShape, fill = color) 
            #img.save( imagesPath + str(counter).zfill(6) + imageType)
            writer.append_data(np.array(img))

    writer.close()

def makeVideo(input, output):
    fileList = []
    for file in sorted(os.listdir(input)):
        complete_path = imagesPath + file
        fileList.append(complete_path)

    writer = imageio.get_writer(output, fps=fps)

    for im in fileList:
        writer.append_data(imageio.imread(im))
    writer.close()

def deleteImages():
    filelist = glob.glob(os.path.join(imagesPath, "*" + imageType))
    for f in filelist:
        os.remove(f)

genImages()
#makeVideo(imagesPath, outputPath)
#deleteImages()
