from flask import Flask, render_template, Response, request, send_from_directory
import os
from picamera import PiCamera
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
camera = PiCamera()
camera.resolution = (1024, 768)  # Adjust as needed
PICTURES_FOLDER = os.path.expanduser('~/Pictures')
os.makedirs(PICTURES_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    """Generate camera frames for live preview."""
    with camera:
        camera.start_preview()
        stream = BytesIO()
        for _ in camera.capture_continuous(stream, format="jpeg", use_video_port=True):
            stream.seek(0)
            frame = stream.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            stream.seek(0)
            stream.truncate()

@app.route('/live_preview')
def live_preview():
    """Route for live preview streaming."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take_photo', methods=['POST'])
def take_photo():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_path = os.path.join(PICTURES_FOLDER, f'{timestamp}.jpg')
    camera.capture(file_path)
    return f"Photo taken and saved as: {file_path}"

@app.route('/photos')
def view_photos():
    files = os.listdir(PICTURES_FOLDER)
    files = [f for f in files if f.endswith('.jpg')]
    return render_template('photos.html', photos=files)

@app.route('/photos/<filename>')
def get_photo(filename):
    return send_from_directory(PICTURES_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
