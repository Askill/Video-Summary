import imageio
import numpy as np
class Exporter:
    fps = 30
    def __init__(self, data, outputPath):
        print("Exporter initiated")
        fps = self.fps
        writer = imageio.get_writer(outputPath, fps=fps)
        for frame in data:
            writer.append_data(np.array(frame))

        writer.close()