
class Config:
    c = {
        "min_area" : 100,
        "max_area" : 40000,
        "threashold" : 8,
        "resizeWidth" : 512,
        "inputPath" : None,
        "outputPath": None,
        "maxLayerLength": 900, 
        "minLayerLength": 20,    
        "tolerance": 10,
        "maxLength": None,
        "ttolerance": 60,
        "videoBufferLength": 500,
        "noiseThreashold": 0.25,
        "noiseSensitivity": 3/4,
        "LayersPerContour": 20,
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
