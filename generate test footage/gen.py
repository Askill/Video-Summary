
import math 
from PIL import Image, ImageDraw 
import random


def getRandomColorString():
    return '#{:06x}'.format(random.randint(0, 256**3))

fps = 30
xmax = 1920
ymax = 1080
# in minutes
length = 1
numberOfEvents = 3



# creating new Image object 
img = Image.new("RGB", (xmax, ymax)) 

for i in range(numberOfEvents):

    objectWidth = (5 + random.randint(0, 5)) * xmax / 100 
    objectHeight = (10 + random.randint(-5, 5)) * ymax / 100

    objectX = random.randint(0, xmax)
    objectY = random.randint(0, ymax)

    objectSpeedX = random.randint( -int(objectWidth) - 1, int(objectWidth) + 1)
    objectSpeedY = random.randint( -int(objectWidth) - 1, int(objectWidth) + 1)
    color = getRandomColorString()

    for j in range(int(fps*length*60 / numberOfEvents)):

        objectX -= objectSpeedX
        objectY -= objectSpeedY

        objectShape = [(objectX, objectY), (objectX + objectWidth, objectY + objectHeight)] 
        
        
        
        # create rectangle image 
        img1 = ImageDraw.Draw(img)   
        
        img1.rectangle(objectShape, fill = color) 

img.show() 

