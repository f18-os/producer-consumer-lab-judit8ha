#!/usr/bin/env python3

import base64
import time
import numpy as np
import threading
import cv2, queue, os


# globals
outputDir    = 'frames'
clipFileName = 'clip.mp4'

# shared queue
extractionQueue = queue.Queue()
displayingQueue = queue.Queue()
display = threading.Semaphore()
extract = threading.Semaphore()

def extractFrames(fileName):
    # Initialize frame count
    #extractionQueue
    count = 0
    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success, image = vidcap.read()

    print("Reading frame {} {} ".format(count, success))
    while success:
        #extract.acquire()
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)
        # encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)
        # add the frame to the buffer
        extractionQueue.put(jpgAsText)
        success, image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1
    print("done extracting!")


def toGrayscale():
    print("changing to grayscale")
    frameEncod = extractionQueue.get()
    extract.release()
    #extract and decode
    frameRaw = base64.b64decode(frameEncod)
    #change to jpeg raw array
    frameJPG = np.asarray(bytearray(frameRaw), dtype=np.uint8)
    #decode to jpeg image
    grayscaleFrame = cv2.imdecode(frameJPG, cv2.COLOR_BGR2GRAY)
    # encode to jpeg format
    retvalue, jpgBW = cv2.imencode('.jpg', grayscaleFrame)
    # encode to base 64
    jpgToText = base64.b64encode(jpgBW)
    # add to display queue
    display.acquire()
    displayingQueue.put(jpgToText)
    print("finished changing to grayscale")


def displayFrames():
    # globals
    #global outputDir, displayingQueue
    count = 0

    frameDelay = 42  # the answer to everything

    while not displayingQueue.empty():
        # get the next frame
        display.release()
        frameAsText = displayingQueue.get()

        # decode the frame
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

        # get a jpg encoded frame
        img = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)

        print("Displaying frame {}".format(count))

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    print("Finished displaying all frames")
    # cleanup the windows
    cv2.destroyAllWindows()


# FORM A RENDERING PIPELINE USING MULTIPLE THREADS

#THREAD1 -> Read frames from a file
reading_thread = threading.Thread(target=extractFrames, args=[clipFileName])
#THREAD2 -> Convert frames from thread1 to grayscale
grayscale_thread = threading.Thread(target=toGrayscale)
#THREAD3 -> Display frames from thread2
display_thread = threading.Thread(target=displayFrames)

reading_thread.start()
grayscale_thread.start()
display_thread.start()


