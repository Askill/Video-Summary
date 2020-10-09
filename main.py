import os
import time
from ContourExctractor import ContourExtractor
from Exporter import Exporter
from LayerFactory import LayerFactory
from Analyzer import Analyzer
from VideoReader import VideoReader
import cv2
#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken für vergleichsbilder

def demo():
    print("startup")
    resizeWidth = 256
    maxLayerLength = 20*30
    minLayerLength = 30
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
    #print("fill Layers")
    #layerFactory.fillLayers(footagePath, resizeWidth)

    Exporter().exportOverlayed(layerFactory.layers,footagePath, os.path.join(os.path.dirname(__file__), "./short.mp4"), resizeWidth)
    print("Total time: ", time.time() - start)

def init():
    print("not needed yet")

if __name__ == "__main__":
    demo()


