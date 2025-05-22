# 😊 Smile Capture

A web application that captures your photo when you **smile**, built using Flask and OpenCV with real-time face and smile detection.

---

## 📸 Overview

**Smile Capture** is a browser-based application that:

- Starts a webcam feed in real-time.
- Detects faces and smiles using Haar Cascades.
- Automatically captures a photo when a strong, genuine smile is detected.
- Stores and displays the captured images.
- Generates a unique 6-digit code for each capture session.

---

## 🔧 Features

- Real-time face and smile detection using OpenCV.
- Smooth fade-in/out animations using CSS.
- Auto-snap photos when a smile is consistently detected.
- Displays captured images with fade-in effects.
- Lightweight and responsive UI.
- Unique code assigned per session for image folder.

---

## 🧠 Tech Stack

- **Frontend**: HTML, CSS (with animation), JavaScript
- **Backend**: Python, Flask
- **Computer Vision**: OpenCV (with Haar cascades for face and smile detection)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Shahid6174/Smile.git
cd Smile
```

### 2. Install Dependencies

Make sure you have Python ≥ 3.8 installed.

It is recommended to use a virtual environment to avoid dependency conflicts:

```bash
# Create virtual environment (on macOS/Linux)
python3 -m venv venv

# or on Windows
python -m venv venv

# Activate the environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Then install dependencies
pip install -r requirements.txt
```

To deactivate the environment when done:

```bash
deactivate
```

### 3. Download Haar Cascade Files (If not already present)

Place the following XML files inside a folder named `dataset/`:

- [`haarcascade_frontalface_default.xml`](https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml)
- [`haarcascade_smile.xml`](https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_smile.xml)

### 4. Run the Application

```bash
python app.py
```

Then open your browser and visit:  
👉 **http://127.0.0.1:5000**

---

## 📁 Project Structure

```
smile-capture/
├── dataset/
│   ├── haarcascade_frontalface_default.xml
│   └── haarcascade_smile.xml
├── static/
│   └── images/
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
└── README.md
```

---

## 📸 Example

- The app captures **3 smiling photos** per session.
- Click **"Show Captured Images"** to view them below the video feed.
- Click **"Done"** to refresh and start a new session with a new code.

---

## ✅ Dependencies

- Flask
- OpenCV (opencv-python)
- NumPy

All dependencies are listed in `requirements.txt`.

---

## 🙌 Acknowledgements

- OpenCV team for powerful real-time computer vision.
- Flask for simple and elegant web development.

---

## 📃 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions are welcome! Whether you're fixing bugs, improving the UI, adding features, or enhancing performance—your help is appreciated.

### How to Contribute

1. **Fork the repository**  
   Click the `Fork` button at the top right of the GitHub page to create your own copy.

2. **Clone your fork**

   ```bash
   git clone https://github.com/Shahid6174/Smile.git
   cd Smile
   ```

3. **Create a new branch**  
   Use a descriptive branch name:

   ```bash
   git checkout -b your-feature-name
   ```

4. **Make your changes**  
   Improve the project by editing files, fixing bugs, or adding new functionality.

5. **Commit your changes**

   ```bash
   git add .
   git commit -m "Add: brief description of your change"
   ```

6. **Push to your forked repository**

   ```bash
   git push origin your-feature-name
   ```

7. **Open a Pull Request**  
   Go to the original repo on GitHub and click **"New Pull Request"**.  
   Describe your changes clearly and link any related issues if applicable.

### Code Guidelines

- Follow the existing formatting and naming conventions.
- Write clear and concise commit messages.
- Test your changes before submitting a pull request.

---
