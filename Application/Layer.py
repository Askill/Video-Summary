import numpy as np
import cv2
import imutils

from kneed import KneeLocator
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class Layer:
    #bounds = [[(x,y,w,h), ],]

    startFrame = None
    lastFrame = None
    length = None

    def __init__(self, startFrame, data, config):
        self.startFrame = startFrame
        self.lastFrame = startFrame
        self.config = config
        self.data = []
        self.bounds = []
        self.bounds.append([data])
        #print("Layer constructed")

    def add(self, frameNumber, data):
        if not self.startFrame + len(self.bounds) < frameNumber:
            if len(self.bounds[self.startFrame - frameNumber]) >= 1:
                self.bounds[self.startFrame - frameNumber].append(data)
        else:
            self.lastFrame = frameNumber
            self.bounds.append([data])

        self.getLength()

    def getLength(self):
        self.length = len(self.bounds)
        return self.length
    
    def fill(self, inputPath, resizeWidth):
        '''reads in the contour data, needed for export'''
        
        cap = cv2.VideoCapture(inputPath) 
        self.data = [None]*len(self.bounds)
        i = 0
        cap.set(1, self.startFrame)
        while i < len(self.bounds):
            ret, frame = cap.read() 
            
            if ret:
                frame = imutils.resize(frame, width=resizeWidth)
                (x, y, w, h) = self.bounds[i]
                self.data[i] = frame[y:y+h, x:x+w]
            i+=1
        cap.release()

    def clusterDelete(self):
        org = self.bounds
        mapped = []
        mapping = []
        clusterCount = 1
        noiseSensitivity = self.config["noiseSensitivity"] 
        noiseThreashold = self.config["noiseThreashold"]
        for i, bounds in enumerate(org):
            for j, bound in enumerate(bounds):
                x = (bound[0] + bound[2]/2) / self.config["w"]
                y = (bound[1] + bound[3]/2) / self.config["w"]

                mapped.append(list((x,y)))
                mapping.append([i,j])

        mapped = np.array(mapped).astype(np.float16)
        labels = []
        centers = []
        kmeans = None

        while True:
            kmeans = KMeans(init="random", n_clusters=clusterCount, n_init=5, max_iter=300, random_state=42)
            kmeans.fit(mapped)
            labels = list(kmeans.labels_)

            if kmeans.n_features_in_ < clusterCount:
                break

            maxm = 0
            for x in set(labels):
                y = labels.count(x)
                if y > maxm:
                    maxm = y

            if maxm > len(mapped)*(noiseSensitivity) and clusterCount+1<=len(kmeans.cluster_centers_):
                clusterCount += 1
            else: 
                centers = kmeans.cluster_centers_
                break

        classed = [[]]
        for i, x in enumerate(list(labels)):
            while len(classed) <= x:
                classed.append([])
            classed[x].append(i)

        dists = []
        for num, cen in enumerate(centers):
            dist = 0
            for i in classed[num]:
                dist += (mapped[i][0]-cen[0])**2 + (mapped[i][1]-cen[1])**2
            dist/=len(classed[num])
            dists.append(dist*1000)

        newContours = [[]]
        for i, dis in enumerate(dists):
            # copy contours which are spread out, delete rest by not yopying them 
            if dis > noiseThreashold:
                for j in classed[i]:
                    x, y = mapping[j]
                    while x >= len(newContours):
                        newContours.append([])
                    while y > len(newContours[x]):
                        newContours[x].append((None, None, None, None))
                    newContours[x].append(org[x][y])      
        
        self.bounds = newContours
        #print(f"{clusterCount} clusters identified {dists}")

        #fig, ax = plt.subplots()
        #x=mapped[:,0]
        #y=mapped[:,1]
        
        #ax.scatter(x, y, labels, s=10, cmap="rainbow")
        #ax.grid(True)
        #plt.show()

        #print("done")

   
