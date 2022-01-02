import os
import time

from Application.Classifiers import *
from Application.Config import Config
from Application.ContourExctractor import ContourExtractor
from Application.Exporter import Exporter
from Application.Importer import Importer
from Application.LayerFactory import LayerFactory
from Application.LayerManager import LayerManager
from Application.VideoReader import VideoReader


def main():
    startTotal = time.time()
    config = Config()

    fileName = "x23.mp4"
    outputPath = os.path.join(os.path.dirname(__file__), "output")
    dirName = os.path.join(os.path.dirname(__file__), "generate test footage")

    config["inputPath"] = os.path.join(dirName, fileName)
    config["outputPath"] = os.path.join(outputPath, fileName)
    config["importPath"] = os.path.join(
        outputPath, fileName.split(".")[0] + ".txt")
    config["w"], config["h"] = VideoReader(config).getWH()

    if not os.path.exists(config["importPath"]):
        contours, masks = ContourExtractor(config).extractContours()
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours, masks)
    else:
        layers, contours, masks = Importer(config).importRawData()
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours, masks)

    layerManager = LayerManager(config, layers)
    layerManager.transformLayers()

    #layerManager.tagLayers()
    layers = layerManager.layers
    if len(layers) == 0:
        exit(1)

    exporter = Exporter(config)
    print(f"Exporting {len(contours)} Contours and {len(layers)} Layers")
    exporter.export(layers, contours, masks, raw=True, overlayed=True)
    print("Total time: ", time.time() - startTotal)


if __name__ == "__main__":
    main()
