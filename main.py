import os
import time
from ContourExctractor import ContourExtractor
from Exporter import Exporter
from LayerFactory import LayerFactory
#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken für vergleichsbilder
# X diff zu den ref bildern aufnehmen
#   zeichen von contour inhalt
#   langes video

def demo():
    print("startup")
    start = time.time()

    footagePath = os.path.join(os.path.dirname(__file__), "./generate test footage/3.MP4")
    contours = ContourExtractor().extractContours(footagePath)
    print("Time consumed in working: ",time.time() - start)
    layerFactory = LayerFactory(contours)
    Exporter().exportOverlayed(layerFactory.layers, os.path.join(os.path.dirname(__file__), "./short.mp4"))

def init():
    print("not needed yet")

if __name__ == "__main__":
    demo()


