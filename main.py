import os
import time
from ContourExctractor import ContourExtractor
from Exporter import Exporter
from LayerFactory import LayerFactory
from Analyzer import Analyzer
from VideoReader import VideoReader
from Config import Config
import cv2
#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken für vergleichsbilder

def demo():
    print("startup")
    start = time.time()
    config = Config()

    config["inputPath"] = os.path.join(os.path.dirname(__file__), "./generate test footage/3.mp4")
    config["outputPath"]  = os.path.join(os.path.dirname(__file__), "./output/short.mp4")

    contours = ContourExtractor(config).extractContours()
    print("Time consumed extracting: ", time.time() - start)
    layerFactory = LayerFactory(config, contours)
    layerFactory.freeData()
    layerFactory.sortLayers()

    Exporter(config).exportOverlayed(layerFactory.layers)
    print("Total time: ", time.time() - start)

def init():
    print("not needed yet")

if __name__ == "__main__":
    demo()


