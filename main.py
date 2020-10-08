import os
import time
from ContourExctractor import ContourExtractor
from Exporter import Exporter
from LayerFactory import LayerFactory
from Analyzer import Analyzer
import cv2
#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken für vergleichsbilder

def demo():
    print("startup")
    resizeWidth = 1024
    maxLayerLength = 1*60*30
    minLayerLength = 3
    start = time.time()

    footagePath = os.path.join(os.path.dirname(__file__), "./generate test footage/3.mp4")
    #analyzer = Analyzer(footagePath)
    #print("Time consumed reading video: ", time.time() - start)
    contours = ContourExtractor().extractContours(footagePath, resizeWidth)
    print("Time consumed in working: ", time.time() - start)
    layerFactory = LayerFactory(contours)
    print("freeing Data", time.time() - start)
    layerFactory.freeData(maxLayerLength, minLayerLength)
    print("sort Layers")
    layerFactory.sortLayers()
    print("fill Layers")
    layerFactory.fillLayers(footagePath, resizeWidth)
    underlay = cv2.VideoCapture(footagePath).read()[1]
    Exporter().exportOverlayed(underlay, layerFactory.layers, os.path.join(os.path.dirname(__file__), "./short.mp4"), resizeWidth)
    print("Total time: ", time.time() - start)

def init():
    print("not needed yet")

if __name__ == "__main__":
    demo()


