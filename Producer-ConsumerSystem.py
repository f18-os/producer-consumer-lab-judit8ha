#!/usr/bin/env python3

import base64
import time
import numpy as np
import threading
import cv2, queue, os


# globals
outputDir    = 'frames'
clipFileName = 'clip.mp4'

# initialize frame count
count = 0
# shared queue
extractionQueue = queue.Queue(10)
displayingQueue = queue.Queue(10)

def extractFrames(fileName):
    # Initialize frame count
    global count, extractionQueue

    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success, image = vidcap.read()

    print("Reading frame {} {} ".format(count, success))
    while True:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)
        # encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)
        # add the frame to the buffer
        extractionQueue.put(jpgAsText)
        success, image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1



def toGrayscale():
    # globals
    global outputDir, count, extractionQueue, displayingQueue

    frame = cv2.imread(base64.b64decode(extractionQueue.get()))
    # get the next frame file name
    inFileName = frame.format(outputDir, count)
    # load the next file
    inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

    while True:
        print("Converting frame {}".format(count))
        # convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
        jpgAsText = base64.b64encode(grayscaleFrame)
        displayingQueue.put(jpgAsText)

        # generate output file name
        #outFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)
        # write output file
        #cv2.imwrite(outFileName, grayscaleFrame)
        frame = cv2.imread(base64.b64decode(outputBuffer.get()))
        # generate input file name for the next frame
        inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)
        # load the next frame
        inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)


def displayFrames():
    # globals
    global outputDir, displayingQueue

    frameDelay = 42  # the answer to everything

    startTime = time.time()

    # Generate the filename for the first frame
    frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

    # load the frame
    frame = cv2.imread(base64.b64decode(displayingQueue.get()))
    #frame = cv2.imread(frameFileName)

    while True:

        print("Displaying frame {}".format(count))
        # Display the frame in a window called "Video"
        cv2.imshow("Video", frame)

        # compute the amount of time that has elapsed
        # while the frame was processed
        elapsedTime = int((time.time() - startTime) * 1000)
        print("Time to process frame {} ms".format(elapsedTime))

        # determine the amount of time to wait, also
        # make sure we don't go into negative time
        timeToWait = max(1, frameDelay - elapsedTime)

        # Wait for 42 ms and check if the user wants to quit
        if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
            break

            # get the start time for processing the next frame
        startTime = time.time()

        # get the next frame filename
        #count += 1
        #frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

        # Read the next frame file
        #frame = cv2.imread(frameFileName)

    # make sure we cleanup the windows, otherwise we might end up with a mess
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


