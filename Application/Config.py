
class Config:
    c = {
        "min_area" : 5000,
        "max_area" : 40000,
        "threashold" : 7,
        "resizeWidth" : 512,
        "inputPath" : None,
        "outputPath": None,
        "maxLayerLength": 1500, 
        "minLayerLength": 40,    
        "tolerance": 20,
        "maxLength": None,
        "ttolerance": 20,
        "videoBufferLength": 500,
        "LayersPerContour": 220,
        "avgNum":10
        }

    def __init__(self):
        '''This is basically just a wrapper for a json / python dict'''
        print("Current Config:")
        for key, value in self.c.items():
            print(f"{key}:\t\t{value}")
    
    def __getitem__(self, key):
        if key not in self.c:
            return None
        return  self.c[key]

    def __setitem__(self, key, value):
        self.c[key] = value
