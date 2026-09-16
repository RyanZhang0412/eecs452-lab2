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
    # Picamera2 "RGB888" buffers are BGR-ordered for OpenCV on this Pi
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_channel = hsv[:, :, 0]
    s_channel = hsv[:, :, 1]

    # H is circular (0..179); orange sits near 0 so wrap-around matters
    diff = np.abs(h_channel.astype(np.int16) - int(color))
    diff = np.minimum(diff, 180 - diff)

    # Low-saturation pixels (gray/beige) are not the ball — push them away
    diff = np.where(s_channel < 50, 255, diff)
    final_img = diff.astype(np.uint8)

    return final_img


def keep_largest_blob(binary, min_area=300):
    """Drop speckles; keep only the largest white region for a stable centroid."""
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if n_labels <= 1:
        return np.zeros_like(binary)

    areas = stats[1:, cv2.CC_STAT_AREA]
    largest_idx = 1 + int(np.argmax(areas))
    if stats[largest_idx, cv2.CC_STAT_AREA] < min_area:
        return np.zeros_like(binary)

    out = np.zeros_like(binary)
    out[labels == largest_idx] = 255
    return out

# Function to find the centroid and radius of a detected region
# Inputs:
#   img         Binary image
#   USE_IDX_IMG Binary flag. If true, use the index image in calculations; if
#               false, use a double nested for loop.
# Outputs:
#   center      2-tuple denoting centroid
#   radius      Radius of found circle
def identify_ball(img, USE_IDX_IMG):
    h, w = img.shape

    if USE_IDX_IMG == False:
        k = 0
        x_sum = 0
        y_sum = 0
        for y in range(h):
            for x in range(w):
                if img[y, x] != 0:
                    x_sum += x
                    y_sum += y
                    k += 1

        if k != 0:
            cx = x_sum / k
            cy = y_sum / k
            radius = int(np.sqrt(k / np.pi))
            center = (int(cx), int(cy))
        else:
            center = (0, 0)
            radius = 0

    else:
        k = np.count_nonzero(img)

        if k == 0:
            return (0, 0), 0

        x_idx = np.expand_dims(np.arange(w), 0)
        y_idx = np.expand_dims(np.arange(h), 1)

        mask = (img > 0).astype(np.float64)
        cx = np.sum(mask * x_idx) / k
        cy = np.sum(mask * y_idx) / k
        radius = int(np.sqrt(k / np.pi))
        center = (int(cx), int(cy))

    return center, radius

# Function to find the centroid and radius of a detected region using OpenCV's
# built-in functions.
# Inputs:
#   img         Binary image
# Outputs:
#   center      2-tuple denoting centroid
#   radius      Radius of found circle
def contours_localization(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return (0, 0), 0

    largest = max(contours, key=cv2.contourArea)
    (x, y), radius = cv2.minEnclosingCircle(largest)
    center = (int(x), int(y))
    radius = int(radius)

    return center, radius

################################
### CONSTANTS AND PARAMETERS ###
################################
USE_IDX_IMG = True   # False = nested loops (very slow, ~0.5–2s/frame); True = NumPy index image (fast)
FTP = True

# Orange ball starting guesses — tune with trackbars while watching Binary Image
H_val = 13
thold_val = 13

# Light smoothing so the green circle doesn't jitter frame-to-frame
SMOOTH_ALPHA = 0.45
_smooth_center = None
_smooth_radius = 0

######################
### INITIALIZATION ###
######################

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

def nothing(x):
    pass

cv2.namedWindow("Trackbars")
cv2.createTrackbar("H-value", "Trackbars", H_val, 179, nothing)
cv2.createTrackbar("Threshold", "Trackbars", thold_val, 255, nothing)

##############
### TIMERS ###
##############

color_threshold_timer = Timer(desc="  color threshold", printflag=FTP)
contours_timer = Timer(desc="  contours", printflag=FTP)
img_disp_timer = Timer(desc="  display images", printflag=FTP)
diff_timer = Timer(desc="    diff image", printflag=FTP)
box_timer = Timer(desc="    box filter", printflag=FTP)
thresh_timer = Timer(desc="    threshold", printflag=FTP)

#################
### MAIN LOOP ###
#################

while True:
    frame_start = time.time()

    H_val = cv2.getTrackbarPos("H-value", "Trackbars")
    thold_val = cv2.getTrackbarPos("Threshold", "Trackbars")

    # capture_array: same pixels as buffer, shape (480, 640, 3)
    # On this Pi, treating it as BGR matches OpenCV display (orange stays orange).
    image = picam2.capture_array("main")
    display_image = image.copy()

    color_threshold_timer.start_time()

    diff_timer.start_time()
    diff_img = color_subtract(image, H_val)
    diff_timer.end_time()

    box_timer.start_time()
    filtered = cv2.boxFilter(diff_img, -1, (5, 5))
    box_timer.end_time()

    thresh_timer.start_time()
    _, thresh = cv2.threshold(filtered, thold_val, 255, cv2.THRESH_BINARY_INV)
    # Morphological cleanup: remove salt noise, fill small holes in the ball
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = keep_largest_blob(thresh, min_area=300)
    thresh_timer.end_time()

    color_threshold_timer.end_time()

    contours_timer.start_time()
    center, radius = identify_ball(thresh, USE_IDX_IMG)

    if radius > 0:
        if _smooth_center is None:
            _smooth_center, _smooth_radius = center, radius
        else:
            a = SMOOTH_ALPHA
            _smooth_center = (
                int(a * center[0] + (1 - a) * _smooth_center[0]),
                int(a * center[1] + (1 - a) * _smooth_center[1]),
            )
            _smooth_radius = int(a * radius + (1 - a) * _smooth_radius)
        draw_c, draw_r = _smooth_center, _smooth_radius
        cv2.circle(display_image, draw_c, draw_r, (0, 255, 0), 2)
    else:
        _smooth_center, _smooth_radius = None, 0
    contours_timer.end_time()

    img_disp_timer.start_time()
    cv2.imshow("Raw Image", display_image)
    cv2.imshow("Difference Image", diff_img)
    cv2.imshow("Binary Image", thresh)
    img_disp_timer.end_time()

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    if key == ord("c"):
        # pyplot expects RGB; OpenCV/Picamera2 buffer here is BGR
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title("Captured Frame (RGB)")
        plt.axis("off")
        plt.show()

    frame_end = time.time()
    elapsed_time = frame_end - frame_start
    print("Frame processed in %.04f s (%02.2f frames per second)" % (elapsed_time, 1.0 / elapsed_time))

cv2.destroyAllWindows()
picam2.stop_encoder()
