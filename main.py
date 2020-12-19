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
    startTotal = time.time()
    start = startTotal
    config = Config()

    fileName = "3.mp4"
    outputPath = os.path.join(os.path.dirname(__file__), "output")
    dirName = os.path.join(os.path.dirname(__file__), "generate test footage")

    config["inputPath"] = os.path.join(dirName, fileName)
    config["outputPath"]  = os.path.join(outputPath, fileName)

    config["importPath"] = os.path.join(outputPath, fileName.split(".")[0] + ".txt")

    config["w"], config["h"] = VideoReader(config).getWH()
    stats = dict()
    if not os.path.exists(config["importPath"]):
        contours, masks = ContourExtractor(config).extractContours()
        stats["Contour Extractor"] = time.time() - start
        start = time.time()

        print("Time consumed extracting contours: ", stats["Contour Extractor"])
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours, masks)
        stats["Layer Factory"] = time.time() - start
        start = time.time()
    else:
        layers, contours, masks = Importer(config).importRawData()
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours, masks)

    layerManager = LayerManager(config, layers)
    layerManager.transformLayers()
    stats["Layer Manager"] = time.time() - start
    start = time.time()

    #layerManager.tagLayers()
    layers = layerManager.layers
    print([len(l) for l in sorted(layers, key = lambda c:len(c), reverse=True)[:20]])
    if len(layers) == 0:
        exit(1)
    exporter = Exporter(config)
    print(f"Exporting {len(contours)} Contours and {len(layers)} Layers")
    exporter.export(layers, contours, masks, raw=True, overlayed=False)
    stats["Exporter"] = time.time() - start

    print("Total time: ", time.time() - startTotal)
    print(stats)
    exit(0)

if __name__ == "__main__":
    main()


