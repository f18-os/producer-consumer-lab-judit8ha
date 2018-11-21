#!/usr/bin/env python3

import base64
import random
import time
import numpy as np
import threading
import cv2, queue, os


# globals
N = 10
clipFileName = 'clip.mp4'
extractionQueue = [10]
displayingQueue = [10]
lock = 0;

eBuffFull = threading.Semaphore()


def extractFrames(fileName,iBuffer):
    # Initialize frame count
    #extractionQueue
    count = 1
    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    #success, image = vidcap.read()

    print("Reading frame {} {} ".format(count, success))

    while True:
        if(iBuffer.isFull()):
            eBuffFull.acquire()


        success, image = vidcap.read()
        success, jpgImage = cv2.imencode('.jpg', image)
        # encode the frame as base 64 to make debugging easier
        #jpgAsText = base64.b64encode(jpgImage)
        # add the frame to the buffer
        iBuffer.put(jpgImage)
        #success, image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1
    print("done extracting!")



def toGrayscale(iBuffer, oBuffer):
    while True:
        print("changing to grayscale")
        frameEncod = iBuffer.get()
        #print(frameEncod)
        #extract.release()
        #extract and decode
        #frameRaw = base64.b64decode(frameEncod)
        #change to jpeg raw array
        frameJPG = np.asarray(bytearray(frameRaw), dtype=np.uint8)
        #decode to jpeg imageqq
        img = cv2.imdecode(frameJPG, cv2.IMREAD_UNCHANGED)
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # encode to jpeg format
        retvalue, jpgBW = cv2.imencode('.jpg', grayscaleFrame)
        # encode to base 64
        jpgToText = base64.b64encode(jpgBW)
        # add to display queue
        #display.acquire()
        oBuffer.put(jpgToText)
    print("finished changing to grayscale")
    grayFinished = True



def displayFrames(oBuffer):
    count = 0
    frameDelay = 42  # the answer to everything
    # display.release()
    frameAsText = oBuffer.get()
    # decode the frame
    #jpgRawImage = base64.b64decode(frameAsText)
    # convert the raw frame to a numpy array
    jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
    # get a jpg encoded frame
    frame = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)
    cv2.imshow("Video", frame)
    while True:
        frameInterval_s = 0.042  # inter-frame interval, in seconds

        nextFrameStart = time.time()

        while frame is not None:
            print("Displaying frame {}".format(count))

            # Display the frame in a window called "Video"
            cv2.imshow("Video", frame)

            # get the next frame filename
            count += 1
            frameFileName = "grayscale_{:04d}.jpg".format(count)

            # Read the next frame file
            frame = cv2.imread(frameFileName)

            # delay beginning of next frame display
            delay_s = nextFrameStart - time.time()
            nextFrameStart += frameInterval_s
            delay_ms = int(max(1, 1000 * delay_s))
            print("delay = %d ms" % delay_ms)
            if cv2.waitKey(delay_ms) and 0xFF == ord("q"):
                break

    print("Finished displaying all frames")
    # cleanup the windows
    cv2.destroyAllWindows()


# FORM A RENDERING PIPELINE USING MULTIPLE THREADS

#THREAD1 -> Read frames from a file
reading_thread = threading.Thread(target=extractFrames, args=[clipFileName, extractionQueue])
#reading_thread.setDaemon(True)
reading_thread.start()
#THREAD2 -> Convert frames from thread1 to grayscale
#grayscale_thread = threading.Thread(target=toGrayscale, args=[extractionQueue, displayingQueue])
#grayscale_thread.setDaemon(True)
#grayscale_thread.start()
#THREAD3 -> Display frames from thread2
display_thread = threading.Thread(target=displayFrames, args=[extractionQueue])
display_thread.start()

reading_thread.join()
#grayscale_thread.join()
display_thread.join()







