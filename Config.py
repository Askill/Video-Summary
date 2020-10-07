
class Config:
    c = {
        "min_area" : 500,
        "max_area" : 28000,
        "threashold" : 13,
        "xDim" : 0,
        "yDim" : 0,
        "resizeWidth" : 512,
        "inputPath" : "",
        "outputPath": "",
        "maxLayerLength": 1000, 
        "minLayerLength": 0,
        "fps": 30,        
        "tolerance": 5,
        "maxLength": None,
        ""
    }
    __init__(self):
        print(Current Config:)
    
    def __getitem__(self, key):
        return  self.c[key]

    def __setitem__(self, key, value):
        return  self.c[key] = value
