# Code adapted from Tensorflow Object Detection Framework
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
# Tensorflow Object Detection Detector

import numpy as np
import tensorflow as tf
import cv2

from Application.Classifiers.ClassifierInterface import ClassifierInterface


class Classifier(ClassifierInterface):
    def __init__(self):
        print("1")
        self.model_path = "./class1.pb"
        self.odapi = DetectorAPI(path_to_ckpt=self.model_path)
        self.threshold = 0.6  

    def detect(self, stream):
        cap = cv2.VideoCapture(stream)
        img = None
        r, img = cap.read()
        if img is None:
            return img
        # scale the image down for faster processing
        scale_percent = 60 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)

        img = cv2.resize(img, dim)

        # get the results from the net
        boxes, scores, classes, num = self.odapi.process_frame(img)
        res = False
        for i in range(len(boxes)):
            # Class 1 represents human
            # draw recogniction boxes and return resulting image + true/false
            if classes[i] == 1:
                if scores[i] > self.threshold:
                    box = boxes[i]
                    cv2.rectangle(img, (box[1], box[0]), (box[3], box[2]), (255, 0, 0), 2)
                    res = True
                    return img, res
                else:
                    res = False
                    return img, res


    def tagLayers(self, layers):
        print("tagging")
    # Detector API can be changed out given the I/O remains the same
    # this way you can use a different N-Net if you like to
    class DetectorAPI:
        def __init__(self, path_to_ckpt):
            self.path_to_ckpt = path_to_ckpt

            self.detection_graph = tf.Graph()
            with self.detection_graph.as_default():
                od_graph_def = tf.GraphDef()
                with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                    serialized_graph = fid.read()
                    od_graph_def.ParseFromString(serialized_graph)
                    tf.import_graph_def(od_graph_def, name='')

            self.default_graph = self.detection_graph.as_default()
            self.sess = tf.Session(graph=self.detection_graph)

            # Definite input and output Tensors for detection_graph
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        def process_frame(self, image):
            # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image, axis=0)
            # Actual detection.

            (boxes, scores, classes, num) = self.sess.run(
                [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                feed_dict={self.image_tensor: image_np_expanded})

            im_height, im_width,_ = image.shape
            boxes_list = [None for i in range(boxes.shape[1])]
            for i in range(boxes.shape[1]):
                boxes_list[i] = (
                    int(boxes[0, i, 0] * im_height),
                    int(boxes[0, i, 1] * im_width),
                    int(boxes[0, i, 2] * im_height),
                    int(boxes[0, i, 3] * im_width)
                )

            return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

        def close(self):
            self.sess.close()
            self.default_graph.close()

