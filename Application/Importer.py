import pickle

class Importer:
    def __init__(self, config):
        self.path = config["importPath"]

    def importRawData(self):
        #print("Loading previous results")
        with open(self.path, "rb") as file:
            layers, contours, masks = pickle.load(file)
        return (layers, contours, masks)