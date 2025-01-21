#!/usr/bin/env python3
from gpiozero import Button
from picamera2 import Picamera2, Preview
import cv2
import numpy as np
from pynput import keyboard
import time

# Function to give a "film look" to the image
def apply_film_look(image):
    # Add a vignette effect
    rows, cols = image.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols / 3)
    kernel_y = cv2.getGaussianKernel(rows, rows / 3)
    kernel = kernel_y * kernel_x.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    vignette = cv2.merge((mask, mask, mask))
    image = cv2.convertScaleAbs(image * vignette / 255)

    # Add film grain
    noise = np.random.normal(0, 20, image.shape).astype(np.uint8)
    image = cv2.add(image, noise)

    # Apply a slight color tint (warmer tones)
    image = cv2.addWeighted(image, 0.9, np.full_like(image, (10, 20, 40)), 0.1, 0)

    # Adjust contrast and brightness
    alpha = 1.2  # Contrast
    beta = 20    # Brightness
    image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    return image

# Function to capture, edit, and save an image
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

    # Apply the film look effect
    edited_frame = apply_film_look(cropped_frame)

    # Save the edited image to a file
    filename = '/home/dsp/Pictures/%03d_film.jpg' % frame
    cv2.imwrite(filename, edited_frame)
    print('Image captured and edited: ' + filename)

# Mouse callback function
def on_mouse(event, x, y, flags, param):
    global frame, show_message, message_time
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        capture_screenshot(frame)
        frame += 1
        # Show "Photo captured" message
        show_message = True
        message_time = time.time()

# Key listener function
def on_press(key):
    global frame, show_message, message_time
    try:
        if key.char == "a":  # Detect the 'a' key press
            capture_screenshot(frame)
            frame += 1
            # Show "Photo captured" message
            show_message = True
            message_time = time.time()
    except AttributeError:
        pass

# Initialize Picamera2 and set up preview
with Picamera2() as picam2:
    frame = int(time.time())
    show_message = False
    message_time = 0

    # Set up OpenCV preview window
    picam2.start_preview(Preview.DRM)  # Use DRM preview for better OpenCV integration
    preview_config = picam2.create_preview_configuration()
    picam2.configure(preview_config)
    picam2.start()
    print("Preview started")

    # Create a named OpenCV window and set the mouse callback
    window_name = "Camera Preview"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, on_mouse)

    # Start listening for key presses
    with keyboard.Listener(on_press=on_press) as listener:
        while True:
            # Capture and display frames in the OpenCV window
            frame_data = picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)

            # Display "Photo captured" message for 2 seconds
            if show_message and (time.time() - message_time < 2):
                cv2.putText(frame_bgr, "Photo captured", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif show_message:
                show_message = False

            cv2.imshow(window_name, frame_bgr)

            # Exit if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Stop key listener and close window
        listener.stop()
        cv2.destroyAllWindows()
