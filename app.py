from flask import Flask, render_template, Response, jsonify, request, send_file
import cv2
import os
import random
import string
import time
import io
import zipfile

app = Flask(__name__)

# Ensure directories exist
os.makedirs('static/images', exist_ok=True)

# Load the face and smile cascade classifiers
face_cascade = cv2.CascadeClassifier('dataset/haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier('dataset/haarcascade_smile.xml')

# Global variables
camera = None
total_images = 3  # Number of images to capture per session
required_frames = 15  # Number of consecutive frames with smile needed to trigger capture

# Store session data
sessions = {}

def generate_random_code():
    """Generate a random 6-digit code for the session folder"""
    return ''.join(random.choices(string.digits, k=6))

def get_camera():
    """Get or initialize the camera"""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def release_camera():
    """Release the camera resource"""
    global camera
    if camera is not None:
        camera.release()
        camera = None

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/capture')
def capture():
    """Render the capture page"""
    # Check if we need a new session
    new_session = request.args.get('new', 'false').lower() == 'true'
    
    # Get or create session code
    if 'code' in request.cookies and not new_session:
        folder_code = request.cookies.get('code')
    else:
        folder_code = generate_random_code()
        
    # Ensure the folder exists
    folder_path = os.path.join('static', 'images', folder_code)
    os.makedirs(folder_path, exist_ok=True)
    
    # Initialize session data if needed
    if folder_code not in sessions:
        sessions[folder_code] = {
            'smile_frames': 0,
            'captured_images': 0,
            'last_capture_time': 0
        }
    
    response = Response(render_template('capture.html', folder_code=folder_code))
    response.set_cookie('code', folder_code)
    return response

@app.route('/gallery')
def gallery():
    """Render the gallery page"""
    return render_template('gallery.html')

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """Generate frames from the camera with smile detection"""
    camera = get_camera()
    
    # Get the session code from cookie
    folder_code = request.cookies.get('code', generate_random_code())
    
    # Ensure session data exists
    if folder_code not in sessions:
        sessions[folder_code] = {
            'smile_frames': 0,
            'captured_images': 0,
            'last_capture_time': 0
        }
    
    session_data = sessions[folder_code]
    folder_path = os.path.join('static', 'images', folder_code)
    os.makedirs(folder_path, exist_ok=True)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Process each face
        for (x, y, w, h) in faces:
            # Draw rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Region of interest for the face
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Detect smiles
            smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
            
            # If smile detected
            if len(smiles) > 0:
                session_data['smile_frames'] += 1
                
                # Draw rectangle around the smile
                for (sx, sy, sw, sh) in smiles:
                    cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 1)
                
                # If enough consecutive frames with smile and cooldown period passed
                if (session_data['smile_frames'] >= required_frames and 
                    session_data['captured_images'] < total_images and
                    time.time() - session_data['last_capture_time'] > 2):
                    
                    # Save the image
                    img_name = f"image_{session_data['captured_images'] + 1}.jpg"
                    img_path = os.path.join(folder_path, img_name)
                    cv2.imwrite(img_path, frame)
                    
                    # Update session data
                    session_data['captured_images'] += 1
                    session_data['last_capture_time'] = time.time()
                    session_data['smile_frames'] = 0
            else:
                # Reset smile counter if no smile detected
                session_data['smile_frames'] = 0
        
        # Encode the frame for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/get_images')
def get_images():
    """Get images for the current session"""
    folder_code = request.cookies.get('code', '')
    folder_path = os.path.join('static', 'images', folder_code)
    
    if not os.path.exists(folder_path):
        return jsonify({'images': []})
    
    images = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
    images.sort()
    
    # Return full paths including the folder code
    image_paths = [f"{folder_code}/{img}" for img in images]
    
    return jsonify({'images': image_paths})

@app.route('/get_images_by_code')
def get_images_by_code():
    """Get images for a specific session code"""
    folder_code = request.args.get('code', '')
    folder_path = os.path.join('static', 'images', folder_code)
    
    if not os.path.exists(folder_path):
        return jsonify({'images': []})
    
    images = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
    images.sort()
    
    return jsonify({'images': images})

@app.route('/download_images')
def download_images():
    """Download all images for a session as a zip file"""
    folder_code = request.args.get('code', '')
    folder_path = os.path.join('static', 'images', folder_code)
    
    if not os.path.exists(folder_path):
        return "No images found", 404
    
    # Create a zip file in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for img in os.listdir(folder_path):
            if img.endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(folder_path, img)
                zf.write(img_path, img)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'smile_capture_{folder_code}.zip'
    )

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        release_camera()
