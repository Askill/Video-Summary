import json
import os


class Config:
    c = {
        "min_area": 300,
        "max_area": 900000,
        "threshold": 7,
        "resizeWidth": 700,
        "inputPath": None,
        "outputPath": None,
        "maxLayerLength": 5000,
        "minLayerLength": 40,
        "tolerance": 20,
        "maxLength": None,
        "ttolerance": 60,
        "videoBufferLength": 250,
        "LayersPerContour": 220,
        "avgNum": 10,
    }

    def __init__(self, config_path):
        """This is basically just a wrapper for a json / python dict"""
        if os.path.isfile(config_path):
            print("using supplied configuration at", config_path)
            # fail if config can not be parsed
            with open(config_path) as file:
                self.c = json.load(file)
        else:
            print("using default configuration")

        print("Current Config:")
        for key, value in self.c.items():
            print(f"{key}:\t\t{value}")

    def __getitem__(self, key):
        if key not in self.c:
            return None
        return self.c[key]

    def __setitem__(self, key, value):
        self.c[key] = value
