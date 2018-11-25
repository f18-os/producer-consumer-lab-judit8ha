#!/usr/bin/env python3

import base64, time, numpy as np, threading, cv2, queue, os, lock



class Extract_Frames:
    count = 0
    # create a semaphore of 10 items to fill
    full_iBuff = threading.Semaphore(10)

    def _init_(self, fileName, iBuffer):
        self.fileName = fileName
        self.iBuffer = iBuffer
        # open video file
        self.vidcap = cv2.VideoCapture(fileName)
        threading.Thread.__init__(fileName, iBuffer)

    def run(self):
        while True:
            # semaphore n-1 available
            self.full_iBuff.acquire()
            vidcap = cv2.VideoCapture(self.fileName)
            success, image = vidcap.read()
            success, jpgImage = cv2.imencode('.jpg', image)
            # add frame to the buffer
            self.iBuffer.put(jpgImage)
            Grayscale.empty_iBuff.release()
            print('Reading frame {} {}'.format(self.count, success))
            self.count += 1
        print("Done Extracting!")

class Grayscale:
    empty_iBuff = threading.Semaphore(0)
    full_oBuff = threading.Semaphore(10)
    count = 0
    def __init__(self, iBuffer, oBuffer):
        self.iBuffer = iBuffer
        self.oBuffer = oBuffer
        threading.Thread._init_(iBuffer, oBuffer)

    def run(self):
        #release full buffer lock
        while True:
            print("Grayscaling frame {}".format(self.count))
            self.full_oBuff.acquire()
            img = self.iBuffer.get()
            Extract_Frames.full_iBuff.release()
            #decode jpg image
            #img = cv2.imdecode(frameEncod, cv2.IMREAD_UNCHANGED)
            #change image to grayScale
            grayScaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.oBuffer.put(grayScaleFrame)
            Display_Frames.empty_oBuff.release()
            self.count += 1
        print("Finished Changing to Grayscale!")


class Display_Frames:
    count = 0
    empty_oBuff = threading.Semaphore(0)

    def _init_(self, oBuffer):
        self.oBuffer = oBuffer
        threading.Thread.__init__(oBuffer)

    def run(self):
        while True:
            Grayscale.full_oBuff.release()
            jpgImg = self.oBuffer.get()
            frame = cv2.imdecode(jpgImg, cv2.IMREAD_UNCHANGED)
            cv2.imshow("Video", frame)
            while self.oBuffer.isEmpty():
                pass
            self.empty_oBuff.acquire()
            frameInterval_s = 0.042
            nextFrameStart = time.time()
            while frame is not None:
                print("Displaying frame {}".format(self.count))
                # Display the frame in a window called "Video"
                cv2.imshow("Video", frame)
                self.count += 1

                # delay beginning of next frame display
                delay_s = nextFrameStart - time.time()
                nextFrameStart += frameInterval_s
                delay_ms = int(max(1, 1000 * delay_s))
                print("delay + %d ms" % delay_s)
                if cv2.waitKey(delay_ms) and 0xFF == ord("q"):
                    break

        print("finished displaying all frames!")
        cv2.destroyAllWindows()



#class AllThreads:

fileName = 'clip.mp4'
inBuffer = queue.Queue()
outBuffer = queue.Queue()

#def __init__(self):
e = Extract_Frames(fileName, inBuffer)
#e.fileName = fileName
#e.iBuffer = inBuffer
extract = threading.Thread(target=e.run())
extract.start()

g = Grayscale(inBuffer, outBuffer)
#g.iBuffer = inBuffer
#g.oBuffer = outBuffer
grayscale = threading.Thread(target=g.run())
grayscale.start()

d = Display_Frames(outBuffer)
#d.oBuffer = outBuffer
display = threading.Thread(target=d.run())
display.start()


#AllThreads()







