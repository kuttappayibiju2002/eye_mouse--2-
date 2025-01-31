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

# Function to take a screenshot based on coordinates
def take_screenshot(top_left, bottom_right, filename='taken_screenshot.png'):
    width = bottom_right[0] - top_left[0]
    height = bottom_right[1] - top_left[1]

    if width <= 0 or height <= 0:
        raise ValueError("Invalid coordinates: bottom-right must be greater than top-left.")

    screenshot = pyautogui.screenshot(region=(top_left[0], top_left[1], width, height))
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")

# Function to handle screenshot in a separate thread
def screenshot_mode():
    global screenshot_active, top_left, bottom_right

    if screenshot_active:  # Check if screenshot mode is already active
        return  # Exit if it is already active

    screenshot_active = True  # Set the flag to indicate screenshot mode is active
    playsound("voice/screenshot mode.mp3")  # Play sound for entering screenshot mode

    # Reset coordinates before recording new clicks
    with coordinates_lock:
        top_left, bottom_right = None, None
    
    # Get the top-left and bottom-right points dynamically
    with coordinates_lock:
        top_left, bottom_right = record_mouse_clicks()
    
    print(f"Final recorded points - Top-left: {top_left}, Bottom-right: {bottom_right}")
    
    # Try to take a screenshot based on the recorded points
    try:
        print("Screenshot mode started")
        screenshot_path = get_unique_filename("/Users/macbook/Desktop/ignite/PROJECTS/eye_mouse/taken_screenshot")
        take_screenshot(top_left, bottom_right, filename=screenshot_path)
        print("Screenshot function ran successfully")

        # Perform OCR and generate response using Gemini on the taken screenshot
        threading.Thread(target=process_screenshot, args=(screenshot_path,)).start()

    except Exception as e:
        print(f"An error occurred while taking a screenshot: {e}")
    finally:
        click_event.clear()
        screenshot_active = False  # Reset the flag after taking the screenshot
        print("Screenshot mode ended, screenshot_active = False")

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
import os

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


# Function to get a unique filename for screenshots
def get_unique_filename(base_name):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.png"

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

            # Detect left eye closed (left-click)
            if (left[0].y - left[1].y) < 0.008 and not screenshot_active:
                pyautogui.click()
                time.sleep(0.5)
                threading.Thread(target=left_click_mode).start()

            # Detect right eye closed (screenshot mode)
            if (right[0].y - right[1].y) < 0.008 and not screenshot_active:
                threading.Thread(target=screenshot_mode).start()

            # Detect both eyes closed (right-click)
            if (left[0].y - left[1].y) < 0.008 and (right[0].y - right[1].y) < 0.008:
                threading.Thread(target=right_click_mode).start()
                time.sleep(0.5)  # Avoid multiple triggers in quick succession

        # Dynamically draw the rectangle as the mouse moves
        if top_left:
            # Draw the rectangle from top-left to current mouse position
            current_position = pyautogui.position()
            cv2.rectangle(frame, top_left, current_position, (0, 255, 0), 2)

        cv2.imshow('Eye Controlled Mouse', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Program interrupted by user. Exiting...")

finally:
    cam.release()
    cv2.destroyAllWindows()
