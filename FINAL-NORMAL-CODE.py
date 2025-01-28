#!/usr/bin/env python3
import os
import time
import tkinter as tk
from PIL import Image, ImageTk
from gpiozero import Button
from libcamera import controls
from picamera2 import Picamera2, Preview

# Define the GPIO pin for the button
button = Button(21)

# Global variables
photo_directory = "/home/pi/Pictures"
frame = 1  # Start frame counter

def get_next_filename():
    """Generate the next available filename in the photo directory."""
    global frame
    while True:
        filename = os.path.join(photo_directory, f"img_{frame:04d}.jpg")
        if not os.path.exists(filename):
            return filename
        frame += 1

def show_confirmation_window(filename):
    """Show a Tkinter window confirming the photo capture."""
    window = tk.Tk()
    window.title("Photo Captured")

    # Full-screen configuration
    window.attributes("-fullscreen", True)
    window.configure(bg="black")

    # Add the message label
    label = tk.Label(window, text="Photo Captured", font=("Helvetica", 36), fg="green", bg="black")
    label.pack(expand=True)

    # Close the window after 2 seconds and show the overlay
    window.after(2000, lambda: show_image_overlay(window, filename))

    # Start the Tkinter main loop
    window.mainloop()

def show_image_overlay(previous_window, filename):
    """Show the captured image in a full-screen Tkinter window."""
    # Close the previous window
    previous_window.destroy()

    # Load the captured image
    img = Image.open(filename)

    # Create a new Tkinter window for the image overlay
    overlay_window = tk.Tk()
    overlay_window.title("Latest Photo")

    # Full-screen configuration
    overlay_window.attributes("-fullscreen", True)
    overlay_window.configure(bg="black")

    # Resize the image to fit the screen
    screen_width = overlay_window.winfo_screenwidth()
    screen_height = overlay_window.winfo_screenheight()
    img = img.resize((screen_width, screen_height), Image.ANTIALIAS)

    # Display the image
    img_tk = ImageTk.PhotoImage(img)
    label = tk.Label(overlay_window, image=img_tk, bg="black")
    label.pack()

    # Keep a reference to avoid garbage collection
    label.image = img_tk

    # Close the overlay window after 2 seconds
    overlay_window.after(2000, overlay_window.destroy)

    # Start the Tkinter main loop for the overlay window
    overlay_window.mainloop()

# Main script
if __name__ == "__main__":
    # Ensure the photo directory exists
    os.makedirs(photo_directory, exist_ok=True)

    with Picamera2() as picam2:
        # Configure the camera
        picam2.start_preview(Preview.QT)
        preview_config = picam2.create_preview_configuration()
        capture_config = picam2.create_still_configuration()
        picam2.configure(preview_config)
        picam2.start()

        # Allow time for the camera to warm up
        time.sleep(1)
        print("Camera preview started")

        # Enable full-time autofocus
        picam2.set_controls({"AfMode": 2, "AfTrigger": 0})

        # Wait for button presses to capture photos
        print("Waiting for button press...")
        while True:
            button.wait_for_press()
            filename = get_next_filename()
            picam2.switch_mode_and_capture_file(capture_config, filename)
            print(f"Image captured: {filename}")

            # Show the confirmation window
            show_confirmation_window(filename)
