import pyautogui
from pynput import mouse
from playsound import playsound


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
        elif bottom_right is None:
            bottom_right = (int(x), int(y))
            print(f"Bottom-right point recorded at: {bottom_right}")
            playsound("voice/bottom-right.mp3")
            return False

# Main function to start the mouse listener
def record_mouse_clicks():
    print("Please click the top-left and bottom-right points...")
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
