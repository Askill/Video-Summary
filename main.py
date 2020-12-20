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
from itertools import product
import csv

def main(v1, v2, v3, v4):

    startTotal = time.time()
    start = startTotal
    config = Config()

    config["ce_average_threads"] = v1
    config["ce_comp_threads"] = v2
    config["lf_threads"] = v3
    config["videoBufferLength"] = v4

    fileName = "X23-1.mp4"
    outputPath = os.path.join(os.path.dirname(__file__), "output")
    dirName = os.path.join(os.path.dirname(__file__), "generate test footage")

    config["inputPath"] = os.path.join(dirName, fileName)
    config["outputPath"]  = os.path.join(outputPath, fileName)

    config["importPath"] = os.path.join(outputPath, fileName.split(".")[0] + ".txt")

    config["w"], config["h"] = VideoReader(config).getWH()

    stats = [config["ce_average_threads"], config["ce_comp_threads"], config["lf_threads"], config["videoBufferLength"]]

    if not os.path.exists(config["importPath"]):
        contours, masks = ContourExtractor(config).extractContours()
        stats.append(time.time() - start)
        start = time.time()

        #print("Time consumed extracting contours: ", stats["Contour Extractor"])
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours, masks)
        stats.append(time.time() - start)
        start = time.time()
    else:
        stats.append(0)
        layers, contours, masks = Importer(config).importRawData()
        layerFactory = LayerFactory(config)
        layers = layerFactory.extractLayers(contours, masks)
        stats.append(time.time() - start)

    layerManager = LayerManager(config, layers)
    layerManager.transformLayers()
    stats.append(time.time() - start)
    start = time.time()

    #layerManager.tagLayers()
    layers = layerManager.layers
    #print([len(l) for l in sorted(layers, key = lambda c:len(c), reverse=True)[:20]])

    exporter = Exporter(config)
    #print(f"Exporting {len(contours)} Contours and {len(layers)} Layers")
    exporter.export(layers, contours, masks, raw=False, overlayed=True)
    stats.append(time.time() - start)

    print("Total time: ", time.time() - startTotal)
    stats.append(time.time() - startTotal)

    with open("bm.csv", "a") as myfile:
        writer = csv.writer(myfile)
        writer.writerow(stats)
    #print(stats)
    

if __name__ == "__main__":
    ass = list(range(1, 16, 2))
    bss = list(range(1, 16, 2))
    css = [16]
    dss = [500]
    params = [ass, bss, css, dss]
    params = list(product(*params))
    counter = 0
    for a,b,c,d in params:
        print(f"{counter}/{len(params)} - {counter/len(params)}  {a, b, c, d}")
        counter += 1
        main(a, b, c, d)

    ass = [16]
    bss = [16]
    css = list(range(1, 16, 4))
    dss = list(range(50, 500, 200)) 
    params = [ass, bss, css, dss]
    params = list(product(*params))
    counter = 0
    for a,b,c,d in params:
        print(f"{counter}/{len(params)} - {counter/len(params)}  {a, b, c, d}")
        counter += 1
        main(a, b, c, d)


