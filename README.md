# Smile Capture Project 😊

## Description
Smile Capture is a project that allows users to capture photos and download them. The main functionality includes the ability to capture images via the webcam and download the images for future use.

## Features
- **Capture Images**: Users can take photos using their webcam.
- **Download Images**: Each captured image has a download icon that allows users to save the image to their device.
- **Responsive UI**: The interface is user-friendly and visually appealing with a smooth interaction.
- **Instant Image Display**: After capturing images, they are displayed with download icons.

## How to Run

Follow these steps below to get this project up and running on your local machine:

### 1. Clone the Repository

To get a local copy of this project, clone the repository using the following command:

git clone https://github.com/your-username/Smile.git

### 2. Navigate to the Project Directory

Once you've cloned the repository, navigate into the project directory:

cd smile-capture


### 3. Set Up a Virtual Environment (Optional but Recommended)

If you want to keep the project dependencies isolated, you can create and activate a virtual environment:

- For Windows:
    python -m venv venv
    venv\Scripts\activate

- For macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate

### 4. Install Dependencies

Install the required dependencies by running the following command:

pip install -r requirements.txt


If you don’t have a `requirements.txt` file, you can manually install the necessary packages (e.g., Flask, OpenCV, etc.) depending on your project.

### 5. Run the Application

Start the application by running:

python app.py


This will launch the Smile Capture application. Open your browser and go to `http://127.0.0.1:5000/` to see the project in action.

### 6. Capture and Download Images

Once the application is running, you can use the webcam interface to capture images. A download icon will appear next to each image, which you can click to save the images to your device.
