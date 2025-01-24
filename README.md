# RaspiDigicam

![alt text](https://github.com/JohanJVillanueva/RaspiDigicam/blob/main/mockup2.jpg?raw=true)

A Raspberry Pi-based digital camera using the Raspberry Pi Camera Module V2 and the Waveshare 3.5" Touchscreen LCD in compliance for our Digital Signal Processing Fair under Polytechnic University of the Philippines

## Prerequisites

This setup is designed to work with Raspberry Pi OS Legacy (Bullseye, 32-bit) as the waveshrae screen only works with that version of the Raspian.

---

## Installation Guide

### I. Install the LCD first

1. Clone the Waveshare LCD driver repository:
   ```bash
   git clone https://github.com/waveshare/LCD-show.git
   ```
2. Navigate to the cloned directory:
   ```bash
   cd LCD-show/
   ```
3. Make the installation script executable:
   ```bash
   chmod +x LCD35-show
   ```
4. Run the installation script:
   ```bash
   ./LCD35-show
   ```

### II. Enable the Camera Module

1. Open the Raspberry Pi configuration file:
   ```bash
   sudo nano /boot/config.txt
   ```
2. Ensure the following lines are configured:
   ```text
   #start_x
   camera_auto_detect=1
   ```
3. Open the Raspberry Pi configuration (GUI), then turn on Legacy Camera support:
   ```text
   sudo raspi-config
   ```
4. Reboot

### III. Test the Camera

Run the following command to test if the camera is working:

```bash
libcamera-hello
```

### IV. Install RaspiDigicam Software

1. Clone the RaspiDigicam repository:
   ```bash
   git clone https://github.com/JohanJVillanueva/RaspiDigicam.git
   ```

---

## Usage

Follow the instructions in the RaspiDigicam repository to set up and use the camera software.
Install the following packages.

1. Pynput
2. ImageTK
3. PIL
4. Tkinter

---

## Additional Resources

- [Waveshare LCD Documentation](https://www.waveshare.com/wiki/Main_Page)
- [Raspberry Pi Camera Module V2 Guide](https://www.raspberrypi.com/documentation/accessories/camera.html)

## Thanks

This project wouldn't be possible if not for Pikon Cam 3D files made by Kevin McAleer, the modifications for the Raspi Cam V2 by Jeff Geerling and my dad for another set of modifications to my liking. Finally, a special mention to Becca Fersace for their Fullframe episode on The Verge way back when!
