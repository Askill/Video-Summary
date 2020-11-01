import os
import time
from Application.ContourExctractor import ContourExtractor
from Application.Exporter import Exporter
from Application.LayerFactory import LayerFactory
from Application.Analyzer import Analyzer
from Application.Config import Config
from Application.Importer import Importer
from Application.VideoReader import VideoReader
from Application.LayerManager import LayerManager
from Application.Classifiers import *

def main():
    start = time.time()
    config = Config()

    config["inputPath"] = os.path.join(os.path.dirname(__file__), "generate test footage/3.mp4")
    config["importPath"] = os.path.join(os.path.dirname(__file__), "output/short.txt")
    config["outputPath"]  = os.path.join(os.path.dirname(__file__), "output/short.mp4")

    vr = VideoReader(config)
    config["w"], config["h"] = vr.getWH()

    if config["importPath"] is None:
        contours = ContourExtractor(config).extractContours()
        print("Time consumed extracting: ", time.time() - start)
        layerFactory = LayerFactory(config)
        
        layers = layerFactory.extractLayers(contours)

    else:
        layers = Importer(config).importRawData()

    layerManager = LayerManager(config, layers)
    layerManager.cleanLayers()

    layerManager.tagLayers()
    layers = layerManager.layers
    exporter = Exporter(config)
    exporter.export(layers, raw=False)
    
    print("Total time: ", time.time() - start)

if __name__ == "__main__":
    main()


