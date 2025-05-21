from flask import Flask, render_template, request, jsonify, send_file
import cv2
import os
import time
import random
import base64
import numpy as np
import zipfile
from io import BytesIO

app = Flask(__name__)

faceCascade = cv2.CascadeClassifier("dataset/haarcascade_frontalface_default.xml")
smileCascade = cv2.CascadeClassifier("dataset/haarcascade_smile.xml")

total_images = 3  
consecutive_smile_frames = 3  # Number of consecutive frames with smile needed
current_smile_streak = 0

# Generate new folder each time
def generate_new_folder():
    folder_code = str(random.randint(100000, 999999))
    folder_path = os.path.join("static/images", folder_code)
    os.makedirs(folder_path, exist_ok=True)
    return folder_code, folder_path

@app.route('/')
def index():
    global folder_code, folder_path, images_captured, current_smile_streak
    folder_code, folder_path = generate_new_folder()  # Regenerate folder
    images_captured = 0  # Reset captured images count
    current_smile_streak = 0
    return render_template('index.html', folder_code=folder_code)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global images_captured, current_smile_streak, folder_path

    # Return if we've captured enough images
    if images_captured >= total_images:
        return jsonify({
            'images_captured': images_captured,
            'smile_detected': False,
            'alert': False,
            'message': 'Session complete! All images captured.'
        })

    data = request.get_json()
    img_data = data['image'].split(',')[1]
    img_bytes = base64.b64decode(img_data)
    npimg = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({
            'images_captured': images_captured,
            'smile_detected': False,
            'alert': False,
            'message': 'Invalid frame'
        })

    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(grayImg, scaleFactor=1.1, minNeighbors=6)

    smile_detected = False
    alert_triggered = False
    message = "Looking for faces..."

    if len(faces) == 0:
        message = "No face detected"
        current_smile_streak = 0
    else:
        message = "Face detected, looking for smile..."
        for (x, y, w, h) in faces:
            if w < 30 or h < 30:
                continue
            roi_gray = grayImg[y:y+h, x:x+w]
            if roi_gray is None or roi_gray.size == 0 or len(roi_gray.shape) != 2:
                continue

            try:
                smiles = smileCascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.8,
                    minNeighbors=22,
                    minSize=(25, 25)
                )
            except Exception:
                continue

            for (sx, sy, sw, sh) in smiles:
                smile_ratio = sw / sh if sh != 0 else 0
                smile_intensity = sw * sh

                if smile_ratio > 1.4 and smile_intensity > 4000:
                    smile_detected = True
                    current_smile_streak += 1
                    message = f"Smile detected! ({current_smile_streak}/{consecutive_smile_frames})"
                    break

            if smile_detected:
                break

        if not smile_detected:
            current_smile_streak = 0
            message = "Face detected, please smile!"

    # Save image if enough smile frames
    if current_smile_streak >= consecutive_smile_frames:
        img_path = os.path.join(folder_path, f"image_{images_captured+1}.jpg")
        cv2.imwrite(img_path, img)
        images_captured += 1
        current_smile_streak = 0
        alert_triggered = True
        message = f"Perfect smile captured! ({images_captured}/{total_images})"

    return jsonify({
        'images_captured': images_captured,
        'smile_detected': smile_detected,
        'alert': alert_triggered,
        'message': message,
        'smile_streak': current_smile_streak,
        'required_streak': consecutive_smile_frames
    })

@app.route('/get_images')
def get_images():
    return jsonify({"images": [f"{folder_code}/image_{i+1}.jpg" for i in range(images_captured)]})

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
        for folder_code in os.listdir(images_root):
            folder_path = os.path.join(images_root, folder_code)
            if os.path.isdir(folder_path):
                images = [f"/static/images/{folder_code}/{img}" for img in os.listdir(folder_path) if img.endswith('.jpg')]
                if images:
                    gallery_data.append({'id': folder_code, 'images': images})
    return render_template('gallery.html', gallery=gallery_data)

# Initialize global variables
images_captured = 0
current_smile_streak = 0

if __name__ == '__main__':
    app.run(debug=True)