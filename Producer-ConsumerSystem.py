#!/usr/bin/env python3

import os
import threading
import cv2
import numpy as np
import base64
import queue
import time

# filename of clip to load
filename = 'clip.mp4'

# shared queues
extractionQueue = queue.Queue()
conversionQueue = queue.Queue()

gets = threading.Semaphore(0)
puts = threading.Semaphore(10)

gets2 = threading.Semaphore(0)
puts2 = threading.Semaphore(10)


def extractFrames(fileName, outputBuffer):
    # Initialize frame count
    count = 0

    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success, image = vidcap.read()

    print("Reading frame {} {} ".format(count, success))

    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        # encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        puts.acquire()
        outputBuffer.put(jpgAsText)
        gets.release()

        success, image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("Frame extraction complete")


def displayFrames(inputBuffer):
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while True:
        # while not inputBuffer.empty():
        # get the next frame
        gets2.acquire()
        frameAsText = inputBuffer.get()
        puts2.release()

        # decode the frame
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

        # get a jpg encoded frame
        img = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)
        frameInterval_s = 0.042
        nextFrameStart = time.time()

        print("Displaying frame {}".format(count))

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow("Video", img)

        # delay beginning of next frame display
        delay_s = nextFrameStart - time.time()
        nextFrameStart += frameInterval_s
        delay_ms = int(max(1, 1000 * delay_s))
        print("delay + %d ms" % delay_s)

        # if cv2.waitKey(42) and 0xFF == ord("q"):
        #    break
        if cv2.waitKey(delay_ms) and 0xFF == ord("q"):
            break

        count += 1

        if count >= 738:
            break

    print("Finished displaying all frames")
    cv2.destroyAllWindows()
    return


# Method for converting the frames to gray scale
def grayScale(inputBuffer, outputBuffer):
    # initialize frame count
    count = 0

    # while inputFrame is not None:
    # while not self.inputBuffer.empty():
    while True:
        print("Converting frame {}".format(count))

        gets.acquire()
        frameAsText = inputBuffer.get()
        puts.release()

        jpgRawImage = base64.b64decode(frameAsText)
        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

        # get a jpg encoded frame
        img = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)
        # jpg = cv2.imencode('.jpg', jpgImage)
        # inputFrame = cv2.imread(jpg, cv2.IMREAD_COLOR)

        # convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        returnValue, jpgImg = cv2.imencode('.jpg', grayscaleFrame)

        # generate output file name
        # outFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

        # encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImg)

        # add the frame to the buffer
        puts2.acquire()
        outputBuffer.put(jpgAsText)
        gets2.release()

        # write output file
        # cv2.imwrite(outFileName, grayscaleFrame)

        count += 1
        if count >= 738:
            break
        # generate input file name for the next frame
        # inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

        # load the next frame
        # inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)


frameThread = threading.Thread(target=extractFrames, args=(filename, extractionQueue)).start()
grayscaleThread = threading.Thread(target=grayScale, args=(extractionQueue, conversionQueue)).start()
displayThread = threading.Thread(target=displayFrames, args=(conversionQueue,)).start()

