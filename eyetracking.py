import cv2
from EyeTracking.tracker import EyeTracker

# initialize the EyeTracker
et = EyeTracker()

# start the camera
cap = cv2.VideoCapture(0)

while True:
    # read a frame from the camera
    ret, frame = cap.read()

    # detect the eyes in the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eyes = et.detect_eyes(gray)

    # if eyes are detected, track the gaze position
    if len(eyes) == 2:
        # get the gaze position
        gaze_pos = et.track(eyes)

        # print the gaze position
        print(gaze_pos)

    # display the frame
    cv2.imshow('frame', frame)

    # break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release the camera and close the window
cap.release()
cv2.destroyAllWindows()
