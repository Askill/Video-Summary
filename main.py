import os
import time
from ContourExctractor import ContourExtractor
from Exporter import Exporter
from LayerFactory import LayerFactory
import cv2
#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken für vergleichsbilder

def demo():
    print("startup")
    resizeWidth = 512
    maxLayerLength = 5*50*30
    start = time.time()

    footagePath = os.path.join(os.path.dirname(__file__), "./generate test footage/3.MP4")
    contours = ContourExtractor().extractContours(footagePath, resizeWidth)
    print("Time consumed in working: ", time.time() - start)
    layerFactory = LayerFactory(contours)
    layerFactory.freeData(maxLayerLength)
    layerFactory.sortLayers()
    layerFactory.fillLayers(footagePath)
    underlay = cv2.VideoCapture(footagePath).read()[1]
    Exporter().exportOverlayed(underlay, layerFactory.layers, os.path.join(os.path.dirname(__file__), "./short.mp4"), resizeWidth)
    print("Total time: ", time.time() - start)
def init():
    print("not needed yet")

if __name__ == "__main__":
    demo()


