#!/usr/bin/env python3

import time, threading, cv2, queue


class Process:

    inBuffer = queue.Queue(10)
    outBuffer = queue.Queue(10)

    semFill = threading.Semaphore(10)
    semTake = threading.Semaphore(0)

    semFillGray = threading.Semaphore(10)
    semTakeGray = threading.Semaphore(0)

    fileName = 'clip.mp4'
    totalFrames = 0
    complete = False


    def extract(self):
        #individual count
        ecount = 0
        #capture the video into images
        vidcap = cv2.VideoCapture(self.fileName)
        success = True
        #as long as there are frames loop
        while success:
            #take -1 from semaphore if it goes negative it waits
            self.semFill.acquire()
            # take one frame from vidcap
            success, image = vidcap.read()
            # add frame to the buffer
            self.inBuffer.put(image)
            #add +1 to take semaphore if >0 ok for gray to take
            self.semTake.release()
            print('Reading frame {} {}'.format(ecount, success))
            ecount += 1

        print("Done Extracting!")
        self.complete = True
        self.totalFrames = ecount


    def grayScale(self):
        #grayscale count
        gcount = 0

        while True:
            #-1 to take if negative wait. queue empty
            self.semTake.acquire()
            # take a frame from buffer
            img = self.inBuffer.get()
            # add 1 to semFill semaphore
            self.semFill.release()
            # change image to grayScale
            grayScaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            #-1 to gray take semaphore if negative queue is full. wait
            self.semFillGray.acquire()
            #add grayscaled frame to outBuffer
            self.outBuffer.put(grayScaleFrame)
            # +1 to takeSem
            self.semTakeGray.release()
            #print msg
            print("Grayscaling frame {}".format(gcount))
            gcount += 1
            if self.complete and self.totalFrames == gcount:
                break

        print("Finished Changing to Grayscale!")


    def display(self):
        dcount = 0
        while True:
            self.semTakeGray.acquire()
            frame = self.outBuffer.get()
            self.semFillGray.release()

            frameInterval_s = 0.042
            nextFrameStart = time.time()
            cv2.imshow('Video', frame)
            # Display the frame in a window called "Video"
            print("Displaying frame {}".format(dcount))
            # delay beginning of next frame display
            delay_s = nextFrameStart - time.time()
            nextFrameStart += frameInterval_s
            delay_ms = int(max(1, 1000 * delay_s))
            print("delay + %d ms" % delay_s)

            if cv2.waitKey(delay_ms) and 0xFF == ord("q"):
                break

            dcount += 1

            if self.complete and self.totalFrames == dcount:
                break

        print("finished displaying all frames!")
        cv2.destroyAllWindows()

    def run(self):
        extracting = threading.Thread(target=self.extract)
        converting = threading.Thread(target=self.grayScale)
        displaying = threading.Thread(target=self.display)
        extracting.start()
        converting.start()
        displaying.start()


video_process = Process()
video_process.run()

