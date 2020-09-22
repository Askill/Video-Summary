import os
import time
from ContourExctractor import ContourExtractor

#TODO
#   finden von relevanten Stellen anhand von zu findenen metriken

def init():
    print("startup")
    footagePath = os.path.join(os.path.dirname(__file__), "./generate test footage/out.mp4")

    start = time.time()
    contourExtractor = ContourExtractor(footagePath)
    print("Time consumed in working: ",time.time() - start)

    contourExtractor.displayContours()



if __name__ == "__main__":
    init()


