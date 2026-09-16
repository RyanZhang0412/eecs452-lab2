# Skeleton code to be filled in by students for EECS 452 ball tracking lab
# Authors:
#   Audrey M. Cooke (Upgraded to PiCamera2 Support)
#   Ben Simpson
#   Siddharth Venkatesan
#   Ashish Nichanametla

###############
### INCLUDE ###
###############
import cv2
import time
from matplotlib import pyplot as plt
from timer import Timer
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

########################
### HELPER FUNCTIONS ###
########################

# Function for performing color subtraction
# Inputs:
#   img     Image to have a color subtracted. shape: (N, M, C)
#   color   Color to be subtracted.  Integer ranging from 0-255
# Output:
#   Grayscale image of the size as img with higher intensity denoting greater color difference. shape: (N, M)
def color_subtract(img, color):

    # TODO: Convert img to HSV format

    # TODO: Extract only h-values (2D Array)

    # TODO: Take the difference of each pixel and the chosen H-value
    # HINT: Pay attention to integer overflow here. What happens when
    # subtracting unsigned ints and the result is negative?
    # Use integer casting before you subtract and take the absolute value, then
    # use it again when you return a 2D array of unsigned ints as your difference image

    # TODO: Take absolute value of the pixels 

    final_img = None

    return final_img

# Function to find the centroid and radius of a detected region
# Inputs:
#   img         Binary image
#   USE_IDX_IMG Binary flag. If true, use the index image in calculations; if
#               false, use a double nested for loop.
# Outputs:
#   center      2-tuple denoting centroid
#   radius      Radius of found circle
def identify_ball(img, USE_IDX_IMG):
    # Find centroid and number of pixels considered valid
    h, w = img.shape

    # Double-nested for loop code
    if USE_IDX_IMG == False:
        k = 0
        x_sum = 0
        y_sum = 0
        for y in range(w):
            for x in range(h):
                #if img[x,y] != 0:    Uncomment this line when editing here
                    # TODO: Calculate x_sum, y_sum, and k
                    pass


        if(k != 0):
            # TODO: Calculate the center and radius using x_sum, y_sum, and k.
            pass
        else:
            # TODO: Don't forget to account for the boundary condition where k = 0.
            pass
        center = (0,0)
        radius = 0

    # Use index image
    else:
        # Calculate number of orange pixels
        k = np.sum(img)

        if k == 0:
            # No orange pixels.  Return some default value
            return (0,0), 0

        # Index image vectors
        x_idx = np.expand_dims(np.arange(w),0)
        y_idx = np.expand_dims(np.arange(h),1)

        # TODO: Calculate the center and radius using the index image vectors
        #       and numpy commands

        center = (0,0)
        radius = 0

    return center, radius

# Function to find the centroid and radius of a detected region using OpenCV's
# built-in functions.
# Inputs:
#   img         Binary image
# Outputs:
#   center      2-tuple denoting centroid
#   radius      Radius of found circle
def contours_localization(img):

    # TODO: Use OpenCV's findContours function to identify contours in img.
    #       Assume the biggest contour is the ball and determine its center and
    #       radius. Do not forget to deal with the boundary case where no
    #       contours are found.

    center, radius = (0,0), 0

    return center, radius

################################
### CONSTANTS AND PARAMETERS ###
################################
# Flag to indicate computation method for localization heuristic
USE_IDX_IMG = False

# Flag for indicating if we want the function timers to print every frame
FTP = True

# Values for color thresholding (default trackbar values)
# TODO: Find and tune these. Uncomment lines below and assign values to variables.
# H_val =   # H-value of ball for difference image
# thold_val =  # Threshold value for difference image

######################
### INITIALIZATION ###
######################

# initialize the camera and grab a reference to the raw camera capture
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(video_config)
encoder = H264Encoder(1000000, repeat=True)
encoder.output = CircularOutput()
picam2.start()
picam2.start_encoder(encoder)
time.sleep(0.1)

#################
### TRACKBARS ###
#################

# Empty callback function for slider updates
def nothing(x):
    pass

# TODO: Make trackbar window

# TODO: Create trackbars. Use variables you defined in the CONSTANTS AND
#       PARAMETERS section to initialize the trackbars. (Section 3.4)

##############
### TIMERS ###
##############

color_threshold_timer = Timer(desc="  color threshold",printflag=FTP)
contours_timer = Timer(desc="  contours",printflag=FTP)
img_disp_timer = Timer(desc="  display images",printflag=FTP)
# TODO: Add timers for difference image calculation, box filtering, and thresholding (Section 4)

#################
### MAIN LOOP ###
#################

# capture frames from the camera
while True:
    frame_start = time.time() # Start timer for whole frame

    #######################
    ### READ INPUT DATA ###
    #######################
    # TODO: Read trackbar positions (Section 3.4)

    # Grab raw NumPy array representing the image
    image = picam2.capture_buffer("main").reshape((480,640,3)).astype(np.uint8)

    ##########################
    ### COLOR THRESHOLDING ###
    ##########################
    color_threshold_timer.start_time()

    thresh = np.zeros_like(image[:, :, 1]) # Delete this line once you add your code (Section 3.2)
    # Calculate difference image
    # TODO: 1) Generate difference image using color subtract function (Section 3.1)
    # TODO: 2) Time function (Section 4)

    # Box filter
    # TODO: 1) Implement box filter (Section 3.3)
    # TODO: 2) Time function (Section 4)

    # Threshold
    # TODO: 1) Threshold (Section 3.2)
    # TODO: 2) Time function (Section 4)

    color_threshold_timer.end_time()

    #########################
    ### BALL LOCALIZATION ###
    #########################
    contours_timer.start_time()
    # Use the heuristic
    center, radius = identify_ball(thresh, USE_IDX_IMG)

    # Draw the circle
    cv2.circle(image,center, radius,(0,255,0),2)
    contours_timer.end_time()

    ####################################################
    ### DISPLAY THE IMAGE, DEAL WITH KEYPRESSES, ETC ###
    ####################################################
    # Show the image
    img_disp_timer.start_time()
    cv2.imshow("Raw Image", image)
    # TODO: Show the difference frame (Section 3.1)
    # Hint: Show the "thresh" image in a new window called "Difference Image"
    # TODO: Show the binary frame (Section 3.2)

    img_disp_timer.end_time()

    # Get keypress
    key = cv2.waitKey(1) & 0xFF
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    # TODO: if the 'c' key is pressed, capture and display the camera image
    # using pyplot (Section 2)

    # Show time to process whole frame
    frame_end = time.time()
    elapsed_time = frame_end-frame_start
    print("Frame processed in %.04f s (%02.2f frames per second)"%(elapsed_time, 1.0/elapsed_time))

# Close all windows
cv2.destroyAllWindows()
picam2.stop_encoder()
