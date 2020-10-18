import os
import time
from Application.ContourExctractor import ContourExtractor
from Application.Exporter import Exporter
from Application.LayerFactory import LayerFactory
from Application.Analyzer import Analyzer
from Application.Config import Config
from Application.Importer import Importer
from Application.VideoReader import VideoReader
#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken für vergleichsbilder

def demo():
    print("startup")
    start = time.time()
    config = Config()


    config["inputPath"] = os.path.join(os.path.dirname(__file__), "generate test footage/3.mp4")
    #config["importPath"] = os.path.join(os.path.dirname(__file__), "output/short.txt")
    config["outputPath"]  = os.path.join(os.path.dirname(__file__), "output/short.mp4")

    vr = VideoReader(config)
    config["w"], config["h"] = vr.getWH()

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


