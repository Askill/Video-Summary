import os
import time
from ContourExctractor import ContourExtractor
from Exporter import Exporter
from LayerFactory import LayerFactory
from Analyzer import Analyzer
from Config import Config
from Importer import Importer
import cv2
#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken für vergleichsbilder

def demo():
    print("startup")
    start = time.time()
    config = Config()

    config["inputPath"] = os.path.join(os.path.dirname(__file__), "generate test footage/3.mp4")
    #config["importPath"] = os.path.join(os.path.dirname(__file__), "output/short.txt")
    config["outputPath"]  = os.path.join(os.path.dirname(__file__), "output/short.mp4")

    if config["importPath"] is None:
        #ana = Analyzer(config)
        #ref = ana.avg
        contours = ContourExtractor(config).extractContours()
        print("Time consumed extracting: ", time.time() - start)
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours)
    else:
        layers = Importer(config).importRawData()

    exporter = Exporter(config)
    exporter.exportRawData(layers)
    exporter.exportLayers(layers)
    
    print("Total time: ", time.time() - start)

def init():
    print("not needed yet")

if __name__ == "__main__":
    demo()


