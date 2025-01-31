# Before running the code, make sure you install the required packages using the following command:
# pip install -r requirements.txt
# final code with all features

import cv2  # Importing OpenCV for computer vision operations
import mediapipe as mp  # Importing MediaPipe for face landmark detection
import pyautogui  # Importing PyAutoGUI for controlling mouse and screen actions
from playsound import playsound
import time
from screenshot_eye import  take_screenshot,record_mouse_clicks
import threading
import subprocess

# Create an Event object
click_event = threading.Event()

screenshot_active = False  # Flag to track if screenshot mode is active

# Function to handle screenshot in a separate thread
def screenshot_mode():
    global screenshot_active
    if screenshot_active:  # Check if screenshot mode is already active
        return  # Exit if it is already active

    screenshot_active = True  # Set the flag to indicate screenshot mode is active
    playsound("voice/screenshot mode.mp3")  # Play sound for entering screenshot mode

    

    # Start the last_update.py program
    last_update_process = subprocess.Popen(["python3", "last_update.py"])
    
    time.sleep(1)
    
    # Reset coordinates before recording new clicks
    global top_left, bottom_right
    top_left = None
    bottom_right = None
    
    # Get the top-left and bottom-right points
    top_left, bottom_right = record_mouse_clicks()
    print(f"Final recorded points - Top-left: {top_left}, Bottom-right: {bottom_right}")
    
    # Try to take a screenshot based on the recorded points
    try:
        print("screenshot mode started")
        take_screenshot(top_left, bottom_right)
        print("screenshot function run successfully")
    except Exception as e:
        print(f"An error occurred while taking a screenshot: {e}")
    finally:
        # Close the last_update.py program
        last_update_process.terminate()
        last_update_process.wait()

        # Reset the event for future use
        click_event.clear()
        screenshot_active = False  # Reset the flag after taking the screenshot
        print("Screenshot mode ended, screenshot_active = flase")


def left_click_mode():
    playsound("voice/left click.mp3")
    click_event.set()



# Initialize the webcam (0 indicates the default camera)
cam = cv2.VideoCapture(1)

# Initialize the MediaPipe face mesh model with refined landmarks
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Get the screen width and height to map the eye movements to the screen
screen_w, screen_h = pyautogui.size()

try:
    # Main loop to continuously capture frames from the webcam
    while True:
        # Read a frame from the webcam
        _, frame = cam.read()
        
        # Flip the frame horizontally to create a mirror effect (easier for eye tracking)
        frame = cv2.flip(frame, 1)
        
        # Convert the frame from BGR (default in OpenCV) to RGB (required by MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame using the face mesh model to detect facial landmarks
        output = face_mesh.process(rgb_frame)
        
        # Get the detected facial landmarks from the output
        landmark_points = output.multi_face_landmarks
        
        # Get the height and width of the frame (used for drawing circles on landmarks)
        frame_h, frame_w, _ = frame.shape

        # Check if any face landmarks were detected in the frame
        if landmark_points:
            # Extract the landmarks from the first detected face
            landmarks = landmark_points[0].landmark
            
            # Iterate through specific landmarks (474 to 478) that correspond to eye movements
            for id, landmark in enumerate(landmarks[474:478]):
                # Calculate the (x, y) position of the landmark on the frame
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                
                # Draw a green circle on the frame at the detected landmark position
                cv2.circle(frame, (x, y), 3, (0, 255, 0))
                
                # If the landmark ID is 1, map its position to the screen coordinates
                if id == 1:
                    screen_x = screen_w * landmark.x
                    screen_y = screen_h * landmark.y
                    # Move the mouse cursor to the mapped position on the screen
                    pyautogui.moveTo(screen_x, screen_y)

            # Get landmarks that represent the upper and lower eyelids for eye-blink detection
            left = [landmarks[145], landmarks[159]]
            
            # Draw circles on the detected eyelid landmarks to visualize them
            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255))
            
            # Check if the distance between the upper and lower eyelid landmarks is small (eye blink)
            if (left[0].y - left[1].y) < 0.01:
                # If a blink is detected, perform a mouse click
                pyautogui.click()
                time.sleep(0.5)
                threading.Thread(target=left_click_mode).start()
                

            right = [landmarks[374], landmarks[386]]
            # Draw circles on the detected eyelid landmarks to visualize them
            for landmark in right:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255))
            
            # Check if the distance between the upper and lower eyelid landmarks is small (eye blink)
            if (right[0].y - right[1].y) < 0.01:
                # If a blink is detected, perform a mouse click

                threading.Thread(target=screenshot_mode).start()
            




        # Display the processed frame in a window titled 'Eye Controlled Mouse'
        # cv2.imshow('Eye Controlled Mouse', frame)
        
        # Check if the 'q' key was pressed to exit the loop (optional way to quit the program)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    # Handle the Ctrl+C event to stop the program gracefully
    print("Program interrupted by user. Exiting...")

finally:
    # Release the webcam resource when the program ends
    cam.release()
    # Close all OpenCV windows
    cv2.destroyAllWindows()
