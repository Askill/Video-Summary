import os
import time
import argparse

from Application.Config import Config
from Application.ContourExctractor import ContourExtractor
from Application.Exporter import Exporter
from Application.HeatMap import HeatMap
from Application.Importer import Importer
from Application.LayerFactory import LayerFactory
from Application.LayerManager import LayerManager
from Application.VideoReader import VideoReader


def main(config):
    start_total = time.time()

    if os.path.exists(config["cachePath"] + "_layers.txt"):
        layers, contours, masks = Importer(config).import_raw_data()
        layers = LayerFactory(config).extract_layers(contours, masks)
    else:
        contours, masks = ContourExtractor(config).extract_contours()
        layers = LayerFactory(config).extract_layers(contours, masks)

    layer_manager = LayerManager(config, layers)
    layer_manager.clean_layers()

    # layerManager.tagLayers()
    if len(layer_manager.layers) == 0:
        exit(1)

    heatmap = HeatMap(
        config["w"], config["h"], [contour for layer in layer_manager.layers for contour in layer.bounds], 1920 / config["resizeWidth"]
    )
    heatmap.show_image()
    #heatmap.save_image(config["outputPath"].split(".")[0] + "_heatmap.png") # not working yet

    print(f"Exporting {len(contours)} Contours and {len(layer_manager.layers)} Layers")
    Exporter(config).export(layer_manager.layers, contours, masks, raw=True, overlayed=True)
    print("Total time: ", time.time() - start_total)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract movement from static camera recording')
    parser.add_argument('input', metavar='input_file', type=str,
                        help='input video to extract movement from')
    parser.add_argument('output', metavar='output_dir', type=str, nargs="?", default="output",
                        help='output directory to save results and cached files into')
    parser.add_argument('config', metavar='config', type=str, nargs="?", default=None,
                        help='relative path to config.json')
    args = parser.parse_args()

    config = Config(args.config)

    input_path = os.path.join(os.path.dirname(__file__), args.input)
    output_path = os.path.join(os.path.dirname(__file__), args.output)

    file_name = input_path.split("/")[-1]

    config["inputPath"] = input_path
    config["outputPath"] = os.path.join(output_path, file_name)
    config["cachePath"] = os.path.join(output_path, file_name.split(".")[0])
    config["w"], config["h"] = VideoReader(config).get_wh()

    main(config)
