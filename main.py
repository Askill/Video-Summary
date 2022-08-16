import os
import time

from Application.Config import Config
from Application.ContourExctractor import ContourExtractor
from Application.Exporter import Exporter
from Application.HeatMap import HeatMap
from Application.Importer import Importer
from Application.LayerFactory import LayerFactory
from Application.LayerManager import LayerManager
from Application.VideoReader import VideoReader


def main(config):
    startTotal = time.time()

    if not os.path.exists(config["importPath"]):
        contours, masks = ContourExtractor(config).extractContours()
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours, masks)
    else:
        layers, contours, masks = Importer(config).importRawData()
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours, masks)

    layerManager = LayerManager(config, layers)
    layerManager.cleanLayers()

    # layerManager.tagLayers()
    if len(layerManager.layers) == 0:
        exit(1)

    heatmap = HeatMap(
        config["w"], config["h"], [contour for layer in layerManager.layers for contour in layer.bounds], 1920 / config["resizeWidth"]
    )
    heatmap.showImage()

    print(f"Exporting {len(contours)} Contours and {len(layerManager.layers)} Layers")
    Exporter(config).export(layerManager.layers, contours, masks, raw=True, overlayed=True)
    print("Total time: ", time.time() - startTotal)


if __name__ == "__main__":
    config = Config()

    fileName = "x23-1.mp4"
    outputPath = os.path.join(os.path.dirname(__file__), "output")
    inputDirPath = os.path.join(os.path.dirname(__file__), "input")

    config["inputPath"] = os.path.join(inputDirPath, fileName)
    config["outputPath"] = os.path.join(outputPath, fileName)
    config["importPath"] = os.path.join(outputPath, fileName.split(".")[0] + ".txt")
    config["w"], config["h"] = VideoReader(config).getWH()

    main(config)
