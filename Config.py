
class Config:
    c = {
        "min_area" : 500,
        "max_area" : 9000,
        "threashold" : 10,
        "resizeWidth" : 512,
        "inputPath" : None,
        "outputPath": None,
        "maxLayerLength": 900, 
        "minLayerLength": 30,    
        "tolerance": 10,
        "maxLength": None,
        "ttolerance": 10,
        "videoBufferLength": 16}

    def __init__(self):
        print("Current Config:", self.c)
    
    def __getitem__(self, key):
        return  self.c[key]

    def __setitem__(self, key, value):
        self.c[key] = value
