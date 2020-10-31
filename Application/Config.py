
class Config:
    c = {
        "min_area" : 500,
        "max_area" : 40000,
        "threashold" : 5,
        "resizeWidth" : 512,
        "inputPath" : None,
        "outputPath": None,
        "maxLayerLength": 900, 
        "minLayerLength": 20,    
        "tolerance": 20,
        "maxLength": None,
        "ttolerance": 60,
        "videoBufferLength": 16,
        "noiseThreashold": 0.1,
        "noiseSensitivity": 3/4,
        "LayersPerContour": 5,
        "averageFrames": 10
        }

    def __init__(self):
        '''This is basically just a wrapper for a json / python dict'''
        print("Current Config:", self.c)
    
    def __getitem__(self, key):
        if key not in self.c:
            return None
        return  self.c[key]

    def __setitem__(self, key, value):
        self.c[key] = value
