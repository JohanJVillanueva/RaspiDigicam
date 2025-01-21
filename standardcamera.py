#!/usr/bin/env python3
from gpiozero import Button
from picamera2 import Picamera2, Preview
import cv2
import numpy as np
from pynput import keyboard
import time

# Function to capture and save an image
def capture_screenshot(frame):
    frame_data = picam2.capture_array()

    # Convert the frame to BGR color space
    frame_bgr = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)

    # Crop the edges to avoid the window (adjust as needed)
    height, width = frame_bgr.shape[:2]
    crop_top = int(height * 0.05)
    crop_bottom = int(height * 0.95)
    crop_left = int(width * 0.05)
    crop_right = int(width * 0.95)

    cropped_frame = frame_bgr[crop_top:crop_bottom, crop_left:crop_right]

    # Save the cropped image to a file
    filename = '/home/dsp/Pictures/%03d.jpg' % frame
    cv2.imwrite(filename, cropped_frame)
    print('Image captured: ' + filename)

# Key listener function
def on_press(key):
    global frame
    try:
        if key.char == "a":  # Detect spacebar press
            capture_screenshot(frame)
            frame += 1
    except AttributeError:
        pass

# Initialize Picamera2 and set up preview
with Picamera2() as picam2:
    frame = int(time.time())

    # Set up QT preview window
    picam2.start_preview(Preview.QT)
    preview_config = picam2.create_preview_configuration()
    picam2.configure(preview_config)
    picam2.start()
    print("Preview started")

    # Start listening for key presses
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()