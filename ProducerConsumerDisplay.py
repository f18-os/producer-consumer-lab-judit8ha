#!/usr/bin/env python3

import base64, time, mumpy as np, threading, cv2, queue, os, lock



class Extract_Frames:
    count = 1
    # create a semaphore of 10
    full_iBuff = threading.Semaphore(10)

    def _init_(self, fileName, iBuffer):
        self.fileName = fileName
        self.iBuffer = iBuffer
        # open video file
        self.vidcap = cv2.VideoCapture(fileName)
        threading.Thread.__init__(fileName, iBuffer)

    def run(self):
        while True:
            self.iBuff.acquire()
            while self.iBuffer.isFull():
                pass

            success, image = self.vidcap.read()
            success, jpgImage = cv2.imencode('.jpg', image)
            # add frame to the buffer
            self.iBuffer.put(jpgImage)
            print('Reading frame {} {}'.format(self.count, success))
            self.count += 1
        print("Done Extracting!")

class Grayscale:
    empty_iBuff = threading.Semaphore(10)
    def __init__(self, iBuffer, oBuffer):
        self.iBuffer = iBuffer
        self.oBuffer = oBuffer
        threading.Thread._init_(iBuffer, oBuffer)

    def run(self):
        #release full buffer lock
        while True:
            Extract_Frames.full_iBuff.release()
            self.empty_iBuff.acquire()
            # pass while buffer is empty
            while self.iBuffer.isEmpty():
                #retrieve a frame from buffer
                frameEncod = self.iBuffer.get()
                #decode jpg image
                img = cv2.imdecode(frameEncod, cv2.IMREAD_UNCHANGED)
                #change image to grayScale
                grayScaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)






