# Producer Consumer Lab


* Three functions
  * One function to extract the frames
  * One function to convert the frames to grayscale
  * One function to display the frames at the original framerate (24fps)
* Each function executes in its own thread
  * The threads execute concurrently

* Threads will need to signal that they have completed their task
    * signaling is achieved by using boolean values.
* Threads must process all frames of the video exactly once
    * All frames are processed exactly once except for the first one. 
* Frames will be communicated between threads using producer/consumer idioms
  * Producer/consumer quesues will be bounded at ten frames
    

