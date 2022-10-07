import pickle
import os.path

class Importer:
    def __init__(self, config):
        self.path = config["cachePath"]

    def import_raw_data(self):
        print("Loading previous results")

        layers = self.load_if_present(self.path + "_layers.txt")
        contours = self.load_if_present(self.path + "_contours.txt")
        masks = self.load_if_present(self.path + "_masks.txt")

        return layers, contours, masks

    def load_if_present(self, path):
        var = None
        if os.path.isfile(path):
            with open(path, "rb") as file:
                var = pickle.load(file)
        else:
            print(path, "file not found")
        return var
