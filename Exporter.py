import imageio
import numpy as np
class Exporter:
    fps = 30

    def __init__(self):
        print("Exporter initiated")

    def export(self, frames, outputPath):
        fps = self.fps
        writer = imageio.get_writer(outputPath, fps=fps)
        for frame in frames:
            writer.append_data(np.array(frame))

        writer.close()
