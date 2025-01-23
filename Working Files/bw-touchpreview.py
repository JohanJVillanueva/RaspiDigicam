#!/usr/bin/env python3
from gpiozero import Button
from picamera2 import Picamera2, Preview
import cv2
import numpy as np
from pynput import mouse
import time
import tkinter as tk
from PIL import Image, ImageTk
import os
from datetime import datetime


def apply_contrast_bw(image, alpha=2.0, beta=50):
    """Convert to high-contrast black and white image."""
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply contrast: alpha (contrast) and beta (brightness)
    contrast_image = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=beta)

    return contrast_image
    

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

    # Apply black and white effect with high contrast
    contrast_bw_frame = apply_contrast_bw(cropped_frame)


    # Get the current date and time
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Add the date and time in the bottom-right corner
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = .5  # Small font size
    font_color = (66, 174, 255)  # Yellow-orange color (BGR format)
    font_thickness = 1

    # Get text size to position it correctly in the bottom-right corner
    text_size = cv2.getTextSize(current_time, font, font_scale, font_thickness)[0]
    text_x = 350
    text_y = 400

    # Put the text on the image
    cv2.putText(contrast_bw_frame, current_time, (text_x, text_y), font, font_scale, font_color, font_thickness)

    # Save the image with effects to a file
    filename = f'/home/dsp/Pictures/{frame:03d}.jpg'
    cv2.imwrite(filename, contrast_bw_frame)
    print('Image captured: ' + filename)
    
        # Show a tkinter window for 2 seconds to indicate the screenshot was taken
    show_confirmation_window(filename)

# Function to show the confirmation window
def show_confirmation_window(filename):
    # Create a tkinter window
    window = tk.Tk()
    window.title("Screenshot Captured")

    # Make the window full-screen
    window.attributes("-fullscreen", True)
    window.configure(bg="black")

    # Add the message label
    label = tk.Label(window, text="Photo captured", font=("Helvetica", 36), fg="green", bg="black")
    label.pack(expand=True)

    # After 2 seconds, close the window
    window.after(2000, lambda: show_image_overlay(window, filename))

    # Start the tkinter main loop
    window.mainloop()

# Function to show the latest image as an overlay
def show_image_overlay(previous_window, filename):
    # Close the previous window
    previous_window.destroy()

    # Load the latest image
    img = Image.open(filename)

    # Get the screen width and height for full-screen display
    screen_width = img.width
    screen_height = img.height

    # Resize the image to fit the screen
    img = img.resize((screen_width, screen_height), Image.ANTIALIAS)

    # Create a Tkinter window to display the image
    overlay_window = tk.Tk()
    overlay_window.title("Latest Screenshot")

    # Make the window full-screen
    overlay_window.attributes("-fullscreen", True)
    overlay_window.configure(bg="black")

    # Display the image in the Tkinter window
    img_tk = ImageTk.PhotoImage(img)
    label = tk.Label(overlay_window, image=img_tk)
    label.pack()

    # Keep a reference to the image object to avoid garbage collection
    label.image = img_tk

    # After 2 seconds, close the overlay window
    overlay_window.after(2000, overlay_window.destroy)

    # Start the tkinter main loop for the overlay window
    overlay_window.mainloop()

# Mouse listener function to detect mouse click
def on_click(x, y, button, pressed):
    global frame, mouse_pressed
    if pressed:
        if not mouse_pressed:  # Ensure we capture the first click
            mouse_pressed = True
            print("Mouse clicked. Waiting for next click to capture the screenshot.")
        else:
            # Trigger screenshot capture when mouse is clicked again
            capture_screenshot(frame)
            frame += 1
            mouse_pressed = False  # Reset after capturing
            print("Captured image, waiting for next click.")

# Initialize Picamera2 and set up preview
with Picamera2() as picam2:
    frame = int(time.time())
    mouse_pressed = False

    # Set up QT preview window
    picam2.start_preview(Preview.QT)
    preview_config = picam2.create_preview_configuration()
    picam2.configure(preview_config)
    picam2.start()
    print("Preview started")

    # Start listening for mouse clicks
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()