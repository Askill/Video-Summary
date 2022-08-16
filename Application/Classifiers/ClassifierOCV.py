import json
import os

import cv2
import numpy as np
import tensorflow as tf

from Application.Classifiers.ClassifierInterface import ClassifierInterface


class Classifier(ClassifierInterface):
    def __init__(self):
        self.threshold = 0.5
        with open(os.path.join(os.path.dirname(__file__), "coco_map.json")) as file:
            mapping = json.load(file)
            self.classes = dict()
            for element in mapping:
                self.classes[element["id"] - 1] = element["display_name"]

        self.net = cv2.dnn.readNet(
            os.path.join(os.path.dirname(__file__), "yolov4.weights"),
            os.path.join(os.path.dirname(__file__), "yolov4.cfg"),
        )
        # self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        # self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.layer_names = self.net.getLayerNames()
        self.outputlayers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        print("Classifier Initiated")

    def tagLayer(self, imgs):
        # get the results from the net
        results = []
        for i, contours in enumerate(imgs[19:20]):
            # print(i)
            for contour in contours:
                height, width, channels = contour.shape

                dim = max(height, width)
                if dim > 320:
                    img2 = np.zeros(shape=[dim, dim, 3], dtype=np.uint8)
                else:
                    img2 = np.zeros(shape=[320, 320, 3], dtype=np.uint8)
                img2[:height, :width] = contour
                blob = cv2.dnn.blobFromImage(img2, 1 / 256, (320, 320), (0, 0, 0), True, crop=False)  # reduce 416 to 320
                self.net.setInput(blob)
                outs = self.net.forward(self.outputlayers)
                for out in outs:
                    for detection in out:
                        scores = detection
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > self.threshold:
                            if self.classes[class_id] not in results:
                                cv2.imshow("changes x", img2)
                                cv2.waitKey(10) & 0xFF
                                results.append(self.classes[class_id])
                            # print(self.classes[x], score)

        return results
