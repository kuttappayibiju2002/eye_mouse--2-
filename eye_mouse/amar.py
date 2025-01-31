import cv2  # Importing OpenCV for computer vision operations
import mediapipe as mp  # Importing MediaPipe for face landmark detection
import pyautogui  # Importing PyAutoGUI for controlling mouse and screen actions
from playsound import playsound
import time
import threading
import google.generativeai as genai
import easyocr
from PIL import Image
from pynput import mouse

# Lock for synchronizing shared variables
coordinates_lock = threading.Lock()

# Create an Event object
click_event = threading.Event()

screenshot_active = False  # Flag to track if screenshot mode is active

# Initialize variables to store points
top_left = None
bottom_right = None

# Function to record mouse clicks
def on_click(x, y, button, pressed):
    global top_left, bottom_right

    if pressed:
        if top_left is None:
            top_left = (int(x), int(y))
            print(f"Top-left point recorded at: {top_left}")
            playsound("voice/top-left.mp3")
        else:
            bottom_right = (int(x), int(y))
            print(f"Bottom-right point recorded at: {bottom_right}")
            playsound("voice/bottom-right.mp3")
            return False

# Main function to start the mouse listener
def record_mouse_clicks():
    print("Please click the top-left point and move the mouse to the bottom-right point...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    return top_left, bottom_right

import os

# Function to take a screenshot based on coordinates and save it to the current directory
def take_screenshot(top_left, bottom_right, filename='taken_screenshot.png'):
    width = bottom_right[0] - top_left[0]
    height = bottom_right[1] - top_left[1]

    if width <= 0 or height <= 0:
        raise ValueError("Invalid coordinates: bottom-right must be greater than top-left.")

    # Get the current working directory
    current_directory = os.getcwd()

    # Save the screenshot to the current directory
    screenshot_path = os.path.join(current_directory, filename)
    screenshot = pyautogui.screenshot(region=(top_left[0], top_left[1], width, height))
    screenshot.save(screenshot_path)
    print(f"Screenshot saved as {screenshot_path}")

# Function to simulate mouse drag using pyautogui
def pyautogui_mouse_drag(start_x, start_y, end_x, end_y, duration=5):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.mouseDown()
    pyautogui.moveTo(end_x, end_y, duration=duration)
    pyautogui.mouseUp()

def screenshot_mode():
    global screenshot_active

    if screenshot_active:
        return  # Exit if screenshot mode is already active

    screenshot_active = True
    print("Screenshot mode activated")

    # Get the current mouse position (top-left corner for the screenshot)
    top_left = pyautogui.position()
    print(f"Top-left corner set to: {top_left}")

    # Define the bottom-right corner at a specific distance from the top-left
    width, height = 400, 300  # You can adjust this as needed
    bottom_right = (top_left[0] + width, top_left[1] + height)
    print(f"Bottom-right corner set to: {bottom_right}")

    # Call the modified take_screenshot function to save the screenshot
    try:
        # Trigger screenshot capture using pyautogui
        print(f"Dragging mouse from {top_left} to {bottom_right}")
        pyautogui_mouse_drag(top_left[0], top_left[1], bottom_right[0], bottom_right[1], duration=5)

        # Save the screenshot to the current directory after it's taken
        screenshot_filename = get_unique_filename("screenshot")
        screenshot_path = os.path.join(os.getcwd(), screenshot_filename)
        take_screenshot(top_left, bottom_right, filename=screenshot_filename)

        # Pass the screenshot path to the process_screenshot function
        process_screenshot(screenshot_path)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        screenshot_active = False
        print("Screenshot mode ended")

def get_unique_filename(base_name):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.png"

# Function to process a screenshot
def process_screenshot(screenshot_path):
    # Step 1: Extract text from the screenshot using EasyOCR
    extracted_text = extract_text_with_easyocr(screenshot_path)
    
    # Step 2: Generate a response using Google Gemini
    generate_response_from_openai(extracted_text)

# Function to extract text from the image using EasyOCR
def extract_text_with_easyocr(image_path):
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader for English language
    result = reader.readtext(image_path)  # Pass the image file path to EasyOCR

    # Extracting the text from the result
    extracted_text = " ".join([text[1] for text in result])
    print("Extracted Text from Image using EasyOCR:")
    print(extracted_text)
    
    return extracted_text

# Function to generate a response from Google Gemini model using Google Generative AI
def generate_response_from_openai(text_prompt):
    genai.configure(api_key="AIzaSyAwJ6rTozBoXQW2K99MZgwU3AzoLrjfxHQ")  # Replace with your actual API key
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Generate content with the model
    response = model.generate_content(text_prompt)
    
    # Access the generated content using the `text` attribute of the response object
    generated_text = response.text.strip()
    print("\nGenerated Response from Google Gemini:")
    print(generated_text)

    # Save the generated response to a text file
    filename = "generated_response.txt"
    with open(filename, 'w') as file:
        file.write(generated_text)
    
    print(f"Response saved to {filename}")
    
    # Automatically open the saved text file
    if os.name == 'nt':  # For Windows
        os.startfile(filename)
    elif os.name == 'posix':  # For macOS and Linux
        os.system(f"open {filename}")
    
    return generated_text

def left_click_mode():
    playsound("voice/left click.mp3")
    click_event.set()

def right_click_mode():
    playsound("voice/right click.mp3")
    pyautogui.click(button='right')

# Initialize the webcam (0 indicates the default camera)
cam = cv2.VideoCapture(1)

# Initialize the MediaPipe face mesh model with refined landmarks
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Get the screen width and height to map the eye movements to the screen
screen_w, screen_h = pyautogui.size()

# Function to handle right-click mode
def right_click_mode():
    playsound("voice/right click.mp3")
    pyautogui.click(button="right")
    print("Right-click executed")

# Main loop to continuously capture frames from the webcam
try:
    while True:
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark
            for id, landmark in enumerate(landmarks[474:478]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))

                if id == 1:
                    screen_x = screen_w * landmark.x
                    screen_y = screen_h * landmark.y
                    pyautogui.moveTo(screen_x, screen_y)

            left = [landmarks[145], landmarks[159]]
            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255))

            right = [landmarks[374], landmarks[386]]
            for landmark in right:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255))

            # Detect both eyes closed (right-click)
            if (left[0].y - left[1].y) < 0.008 and (right[0].y - right[1].y) < 0.008:
                threading.Thread(target=right_click_mode).start()
                time.sleep(2)  # Avoid multiple triggers in quick succession

            # Detect left eye closed (left-click)
            if (left[0].y - left[1].y) < 0.008 and not screenshot_active:
                pyautogui.click()
                time.sleep(0.5)
                threading.Thread(target=left_click_mode).start()

            # Detect right eye closed (screenshot mode)
            if (right[0].y - right[1].y) < 0.008 and not screenshot_active:
                threading.Thread(target=screenshot_mode).start()

            # Detect both eyes fully open (stop the program)
            if (left[0].y - left[1].y) > 5 and (right[0].y - right[1].y) > 5:
                print("Both eyes are fully open. Stopping the program...")
                break  # Exit the loop and stop the program

        # Dynamically draw the rectangle as the mouse moves
        if top_left:
            # Draw the rectangle from top-left to current mouse position
            current_position = pyautogui.position()
            cv2.rectangle(frame, top_left, current_position, (0, 255, 0), 2)

        # cv2.imshow('Eye Controlled Mouse', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Program interrupted by user. Exiting...")

finally:
    cam.release()
    cv2.destroyAllWindows()