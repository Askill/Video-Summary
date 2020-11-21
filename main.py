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

    fileName = "x23.mp4"
    outputPath = os.path.join(os.path.dirname(__file__), "output")
    dirName = os.path.join(os.path.dirname(__file__), "generate test footage")

    config["inputPath"] = os.path.join(dirName, fileName)
    config["outputPath"]  = os.path.join(outputPath, fileName)

    config["importPath"] = os.path.join(outputPath, fileName.split(".")[0] + ".txt")

    config["w"], config["h"] = VideoReader(config).getWH()

    if not os.path.exists(config["importPath"]):
        contours = ContourExtractor(config).extractContours()
        print("Time consumed extracting: ", time.time() - start)
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours)
    else:
        layers, contours = Importer(config).importRawData()
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours)

    layerManager = LayerManager(config, layers)
    layerManager.transformLayers()

    #layerManager.tagLayers()
    layers = layerManager.layers
    exporter = Exporter(config)
    print(f"Exporting {len(contours)} Contours and {len(layers)} Layers")
    exporter.export(layers, contours, raw=True, overlayed=True)
    
    print("Total time: ", time.time() - start)
    exit(0)

if __name__ == "__main__":
    main()


