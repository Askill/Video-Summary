import pickle

class Importer:
    def __init__(self, config):
        self.path = config["importPath"]

    def importRawData(self):
        with open(self.path, "rb") as file:
            layers = pickle.load(file)
        return layers