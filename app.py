import base64
import os
import random
import time
import zipfile
from io import BytesIO

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)

# Ensure these paths are correct and the XML files exist in your 'dataset' folder
faceCascade = cv2.CascadeClassifier("dataset/haarcascade_frontalface_default.xml")
smileCascade = cv2.CascadeClassifier("dataset/haarcascade_smile.xml")

total_images = 3
consecutive_smile_frames = 3  # Number of consecutive frames with smile needed
current_smile_streak = 0

# Global variables (managed by Flask's app context or simply as globals for this simple app)
folder_code = None
folder_path = None
images_captured = 0

# Generate new folder each time a new session starts
def generate_new_folder():
    folder_code = str(random.randint(100000, 999999))
    folder_path = os.path.join("static", "images", folder_code) # Corrected path
    os.makedirs(folder_path, exist_ok=True)
    return folder_code, folder_path

@app.route('/')
def index():
    global folder_code, folder_path, images_captured, current_smile_streak
    folder_code, folder_path = generate_new_folder()  # Regenerate folder for each new session
    images_captured = 0  # Reset captured images count for new session
    current_smile_streak = 0 # Reset smile streak
    return render_template('index.html', folder_code=folder_code)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global images_captured, current_smile_streak, folder_path

    # Early exit if enough images are already captured
    if images_captured >= total_images:
        return jsonify({
            'images_captured': images_captured,
            'smile_detected': False,
            'alert': False,
            'message': 'Session complete! All images captured.'
        })

    data = request.get_json()
    img_data = data['image'].split(',')[1] # Extract base64 data
    img_bytes = base64.b64decode(img_data)
    npimg = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR) # Decode to OpenCV image format

    threshold = float(request.json.get('threshold', 50)) / 100  # Convert percentage to decimal
    
    if img is None:
        return jsonify({
            'images_captured': images_captured,
            'smile_detected': False,
            'alert': False,
            'message': 'Invalid frame received.'
        })

    # Resize image for faster processing (optional, but recommended for live feed)
    # img_height, img_width = img.shape[:2]
    # scale_percent = 70 # percent of original size
    # width = int(img_width * scale_percent / 100)
    # height = int(img_height * scale_percent / 100)
    # dim = (width, height)
    # img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)


    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Equalize histogram for better contrast, especially in varying lighting
    grayImg = cv2.equalizeHist(grayImg)

    faces = faceCascade.detectMultiScale(
        grayImg,
        scaleFactor=1.1, # Keep this reasonable for faces
        minNeighbors=5,  # Reduced from 6, more lenient face detection
        minSize=(60, 60), # Minimum size for face detection
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    smile_detected_in_frame = False # Flag for current frame
    message = "Looking for faces..."

    if len(faces) == 0:
        message = "No face detected."
        current_smile_streak = 0 # Reset streak if face is lost
    else:
        message = "Face detected, looking for smile..."
        for (x, y, w, h) in faces:
            # Draw rectangle around face (for debugging, can be removed)
            # cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Define ROI for mouth/smile within the face
            # Typically, smiles are in the lower half of the face
            roi_gray = grayImg[y + h//2 : y + h, x : x + w] # Lower half of the face
            # roi_color = img[y + h//2 : y + h, x : x + w] # If you need color ROI

            if roi_gray is None or roi_gray.size == 0 or len(roi_gray.shape) != 2:
                continue # Skip if ROI is invalid

            try:
                # Smile detection with parameters scaled by threshold
                # Lower threshold = more sensitive (catches subtle smiles)
                # Higher threshold = less sensitive (requires clear smiles)
                smiles = smileCascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.1,  # Keep constant as it affects the image pyramid
                    minNeighbors=int(35 - threshold * 25),  # Range: 10 (sensitive) to 35 (strict)
                    minSize=(int(25 * (1 - threshold * 0.4)), int(15 * (1 - threshold * 0.4))),  # Smaller size for lower threshold
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
            except Exception as e:
                # Log error but don't stop process
                print(f"Error in smile detection: {e}")
                continue

            for (sx, sy, sw, sh) in smiles:
                # Draw rectangle around smile (for debugging, can be removed)
                # cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)

                # Adjusted smile metrics for better accuracy
                smile_area_ratio = (sw * sh) / (w * h) # Ratio of smile area to face area
                aspect_ratio = sw / sh if sh != 0 else 0

                # Fine-tuned thresholds based on common smile characteristics
                # A smile usually has a wider aspect ratio (horizontal)
                # and occupies a certain proportion of the face area.
                if aspect_ratio > 1.0 and smile_area_ratio > 0.03: # Example: aspect > 1.0 (wider than tall) and area > 3% of face
                    smile_detected_in_frame = True
                    break # Found a smile in this face, no need to check others

            if smile_detected_in_frame:
                break # Found a smile in one of the faces, no need to check other faces

    if smile_detected_in_frame:
        current_smile_streak += 1
        message = f"Smile detected! ({current_smile_streak}/{consecutive_smile_frames})"
    else:
        current_smile_streak = 0 # Reset streak if no smile is detected in current frame
        if len(faces) > 0:
            message = "Face detected, please smile!"
        # Message for "No face detected" is handled above.

    alert_triggered = False
    # Save image if enough smile frames
    if current_smile_streak >= consecutive_smile_frames:
        # Before saving, you might want to convert img back to PNG if you prefer lossless
        # or reduce JPEG quality to save space if needed.
        # For simplicity, saving as JPEG with default quality.
        if not os.path.exists(folder_path): # Just a double check
            os.makedirs(folder_path, exist_ok=True)
        img_path = os.path.join(folder_path, f"image_{images_captured+1}.jpg")
        cv2.imwrite(img_path, img) # Save the original color image
        images_captured += 1
        current_smile_streak = 0 # Reset streak after capturing an image
        alert_triggered = True
        message = f"Perfect smile captured! ({images_captured}/{total_images})"


    return jsonify({
        'images_captured': images_captured,
        'smile_detected': smile_detected_in_frame, # Send actual detection status of current frame
        'alert': alert_triggered,
        'message': message,
        'smile_streak': current_smile_streak,
        'required_streak': consecutive_smile_frames
    })

@app.route('/get_images')
def get_images():
    # Ensure folder_code is defined. If page is refreshed directly to /get_images without going through /,
    # folder_code might be None. Handle this gracefully.
    if folder_code is None:
        return jsonify({"images": []}) # Return empty if no session active

    # Get images for the current session's folder
    current_session_images = []
    if os.path.exists(folder_path):
        for img_name in sorted(os.listdir(folder_path)): # Sort for consistent order
            if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                current_session_images.append(f"{folder_code}/{img_name}")
    return jsonify({"images": current_session_images})


@app.route('/download_images')
def download_images():
    global folder_code, folder_path, images_captured
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for i in range(images_captured):
                img_filename = f"image_{i+1}.jpg"
                img_path = os.path.join(folder_path, img_filename)
                if os.path.exists(img_path):
                    zipf.write(img_path, arcname=img_filename)
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{folder_code}_images.zip"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/gallery')
def gallery():
    gallery_data = []
    images_root = os.path.join('static', 'images')
    if os.path.exists(images_root):
        # Iterate through all subdirectories in 'static/images'
        for folder_code_entry in os.listdir(images_root):
            folder_path_entry = os.path.join(images_root, folder_code_entry)
            if os.path.isdir(folder_path_entry):
                images = []
                # List images in the current folder, ensuring they are valid image files
                for img_name in sorted(os.listdir(folder_path_entry)): # Sort for consistent order
                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        images.append(f"/static/images/{folder_code_entry}/{img_name}")
                if images:
                    gallery_data.append({'id': folder_code_entry, 'images': images})
    
    # Sort gallery_data by id (folder_code) in descending order to show latest first
    gallery_data.sort(key=lambda x: x['id'], reverse=True)

    return render_template('gallery.html', gallery=gallery_data)

@app.route('/edit_image', methods=['POST'])
def edit_image():
    data = request.get_json()
    session_id = data['session_id']
    image_path = data['image_path']
    image_data = data['image_data']

    # Extract the filename from the image path
    filename = os.path.basename(image_path)
    folder_path = os.path.join('static', 'images', session_id)
    if not os.path.exists(folder_path):
        return jsonify({'success': False, 'error': 'Session not found'})

    img_bytes = base64.b64decode(image_data.split(',')[1])
    img_file_path = os.path.join(folder_path, filename)
    with open(img_file_path, 'wb') as f:
        f.write(img_bytes)
    return jsonify({'success': True})


# Initialize global variables for the first run or if not set by Flask
# (This part is often better handled with Flask's app context or Blueprint setup for larger apps)
# For this simple example, it's fine here, but ensure they are correctly managed.
# The @app.route('/') effectively initializes them on each page load.
if __name__ == '__main__':

    # Ensure the base static/images directory exists
    os.makedirs("static/images", exist_ok=True)

    app.run(debug=True, host="0.0.0.0", port=5000)