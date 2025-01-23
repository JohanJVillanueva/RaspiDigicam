#!/usr/bin/env python3
from gpiozero import Button
from picamera2 import Picamera2, Preview
import cv2
import numpy as np
from flask import Flask, render_template, send_from_directory
from pynput import keyboard
import time
import os

# Flask app setup
app = Flask(__name__)
PICTURES_FOLDER = '/home/dsp/Pictures'

# Flask route to display the gallery
@app.route('/')
def gallery():
    # List all image files in the pictures folder
    images = [f for f in os.listdir(PICTURES_FOLDER) if f.endswith(('.jpg', '.png'))]
    images.sort(reverse=True)  # Show the latest photos first
    return render_template('gallery.html', images=images)

# Route to serve images
@app.route('/images/<filename>')
def images(filename):
    return send_from_directory(PICTURES_FOLDER, filename)

# Function to capture and save a normal image
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

    # Save the normal image to a file
    filename = os.path.join(PICTURES_FOLDER, f'{frame:03d}.jpg')
    cv2.imwrite(filename, cropped_frame)
    print('Image captured and saved: ' + filename)

# Mouse callback function
def on_mouse(event, x, y, flags, param):
    global frame
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        capture_screenshot(frame)
        frame += 1

# Key listener function
def on_press(key):
    global frame
    try:
        if key.char == "a":  # Detect the 'a' key press
            capture_screenshot(frame)
            frame += 1
    except AttributeError:
        pass

# Start Flask in a separate thread
def start_web_server():
    from threading import Thread
    server_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
    server_thread.daemon = True
    server_thread.start()

# Picamera2 setup
if __name__ == '__main__':
    frame = int(time.time())
    os.makedirs(PICTURES_FOLDER, exist_ok=True)
    start_web_server()
    print('Web server started at http://<your-raspberry-pi-ip>:5000')

    with Picamera2() as picam2:
        picam2.start_preview(Preview.DRM)
        preview_config = picam2.create_preview_configuration()
        picam2.configure(preview_config)
        picam2.start()
        print("Camera preview started")

        window_name = "Camera Preview"
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, on_mouse)

        with keyboard.Listener(on_press=on_press) as listener:
            while True:
                # Display the live preview in the OpenCV window
                frame_data = picam2.capture_array()
                frame_bgr = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)
                cv2.imshow(window_name, frame_bgr)

                if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on 'q' key press
                    break

            listener.stop()
            cv2.destroyAllWindows()
