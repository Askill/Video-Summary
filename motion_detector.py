from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2


import traceback
import _thread



def compare():
    try:
        url = "1.mp4"

        min_area = 100
        max_area = 30000

        threashold = 10

        # initialize the first frame in the video stream
        vs = cv2.VideoCapture(url)

        res = vs.read()[0]
        firstFrame = None
        # loop over the frames of the video
        while res:

            res, frame = vs.read()

            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            cv2.imshow( "frame", frame )  
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (31, 31), 0)

            # if the first frame is None, initialize it
            if firstFrame is None:
                firstFrame = gray
                continue

            frameDelta = cv2.absdiff(gray, firstFrame)

            thresh = cv2.threshold(frameDelta, threashold, 255, cv2.THRESH_BINARY)[1]


            # dilate the thresholded image to fill in holes, then find contours
            thresh = cv2.dilate(thresh, None, iterations=3)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # loop over the contours
            for c in cnts:
                if cv2.contourArea(c) < min_area or cv2.contourArea(c) > max_area:
                    continue

                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"


            cv2.imshow( "annotated", frame )  
            print("1")

            cv2.waitKey(10) & 0XFF

    except Exception as e: 
        traceback.print_exc()
        
compare()
