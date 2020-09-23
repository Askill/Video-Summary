import os
import time
from ContourExctractor import ContourExtractor
from Exporter import Exporter
#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken für vergleichsbilder
#   diff zu den ref bildern aufnehmen
#   zeichenn on contour inhalt
#   langes video

def demo():
    print("startup")
    footagePath = os.path.join(os.path.dirname(__file__), "./generate test footage/out.mp4")

    start = time.time()
    contourExtractor = ContourExtractor(footagePath)
    print("Time consumed in working: ",time.time() - start)

    frames = contourExtractor.displayContours()
    #exporter = Exporter(frames,os.path.join(os.path.dirname(__file__), "./short.mp4"))

def init():
    print("not needed yet")

if __name__ == "__main__":
    demo()


