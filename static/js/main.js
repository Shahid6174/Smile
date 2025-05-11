document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const startBtn = document.getElementById("start-btn")
  const showImagesBtn = document.getElementById("show-images-btn")
  const doneBtn = document.getElementById("done-btn")
  const backBtn = document.getElementById("back-btn")
  const downloadAllBtn = document.getElementById("download-all")
  const sessionCodeElement = document.getElementById("session-code")
  const statusMessage = document.getElementById("status-message")
  const appContainer = document.querySelector(".app-container")
  const galleryContainer = document.getElementById("gallery")
  const imagesContainer = document.getElementById("images-container")
  const faceGuide = document.querySelector(".face-guide")
  const smileIndicator = document.getElementById("smile-indicator")
  const smileProgress = document.querySelector(".smile-progress")
  const dots = document.querySelectorAll(".dot")

  // App State
  const sessionCode = sessionCodeElement.textContent || ""
  let capturedImages = 0
  let smileDetectionActive = false
  let smileFrameCount = 0
  const totalRequiredFrames = 15 // Number of frames with smile to trigger capture
  const totalImages = 3 // Total images to capture

  // Initialize the app
  function init() {
    updateCaptureProgress()

    // Set up event listeners
    startBtn.addEventListener("click", startCamera)
    showImagesBtn.addEventListener("click", showGallery)
    doneBtn.addEventListener("click", resetSession)
    backBtn.addEventListener("click", hideGallery)
    downloadAllBtn.addEventListener("click", downloadAllImages)

    // Check if we already have images
    checkForExistingImages()
  }

  // Check if there are already images for this session
  function checkForExistingImages() {
    fetch("/get_images")
      .then((response) => response.json())
      .then((data) => {
        if (data.images && data.images.length > 0) {
          capturedImages = data.images.length
          updateCaptureProgress()
          showImagesBtn.disabled = false
          statusMessage.textContent = `${capturedImages} images already captured`
        }
      })
      .catch((err) => {
        console.error("Error checking for existing images:", err)
      })
  }

  // Start the camera
  function startCamera() {
    faceGuide.style.display = "block"
    smileIndicator.style.display = "block"
    startBtn.textContent = "Camera Active"
    startBtn.disabled = true
    statusMessage.textContent = "Position your face and smile naturally"

    // In this version, the camera is already running via Flask's video_feed
    // We just need to start the smile detection simulation
    startSmileDetection()
  }

  // Simulate smile detection (in real app, this would be handled by the backend)
  function startSmileDetection() {
    smileDetectionActive = true

    // This is a simulation - in the real app, this would be handled by the backend
    // For demo purposes, we'll simulate smile detection with random progress
    const simulateSmileDetection = () => {
      if (!smileDetectionActive) return

      // Simulate smile detection progress
      if (capturedImages < totalImages) {
        // Random progress simulation
        if (Math.random() > 0.7) {
          smileFrameCount++
          const progress = (smileFrameCount / totalRequiredFrames) * 100
          smileProgress.style.width = `${progress}%`

          if (smileFrameCount >= totalRequiredFrames) {
            captureImage()
            smileFrameCount = 0
            smileProgress.style.width = "0%"
          }
        }

        requestAnimationFrame(simulateSmileDetection)
      } else {
        completeCapture()
      }
    }

    simulateSmileDetection()
  }

  // Capture an image
  function captureImage() {
    capturedImages++
    updateCaptureProgress()

    // Update status
    statusMessage.textContent = `Smile captured! (${capturedImages}/${totalImages})`

    // In the real app, this would trigger the backend to save the image
    // For demo purposes, we'll simulate a capture with a flash effect
    const flash = document.createElement("div")
    flash.style.position = "absolute"
    flash.style.top = "0"
    flash.style.left = "0"
    flash.style.width = "100%"
    flash.style.height = "100%"
    flash.style.backgroundColor = "white"
    flash.style.opacity = "0.8"
    flash.style.zIndex = "10"
    flash.style.transition = "opacity 0.5s ease"

    document.querySelector(".video-container").appendChild(flash)

    setTimeout(() => {
      flash.style.opacity = "0"
      setTimeout(() => flash.remove(), 500)
    }, 100)

    // Enable the show images button after first capture
    if (capturedImages === 1) {
      showImagesBtn.disabled = false
    }

    // If all images captured, complete the session
    if (capturedImages >= totalImages) {
      completeCapture()
    }
  }

  // Update the capture progress indicators
  function updateCaptureProgress() {
    dots.forEach((dot, index) => {
      if (index < capturedImages) {
        dot.classList.add("active")
      } else {
        dot.classList.remove("active")
      }
    })
  }

  // Complete the capture session
  function completeCapture() {
    smileDetectionActive = false
    statusMessage.textContent = 'All smiles captured! Click "Show Captured Images"'
    smileIndicator.style.display = "none"
    faceGuide.style.display = "none"
    showImagesBtn.classList.add("pulse")
  }

  // Show the gallery of captured images
  function showGallery() {
    appContainer.classList.add("hidden")
    galleryContainer.classList.remove("hidden")
    galleryContainer.classList.add("fade-in")

    // Clear previous images
    imagesContainer.innerHTML = ""

    // Fetch images from the backend
    fetch("/get_images")
      .then((response) => response.json())
      .then((data) => {
        if (data.images && data.images.length > 0) {
          data.images.forEach((image, index) => {
            const imageCard = document.createElement("div")
            imageCard.className = "image-card"

            imageCard.innerHTML = `
              <img src="/static/images/${image}" alt="Captured smile ${index + 1}">
              <div class="image-info">
                <p>Smile ${index + 1} of ${data.images.length}</p>
              </div>
            `

            imagesContainer.appendChild(imageCard)
          })
        } else {
          imagesContainer.innerHTML = '<div class="no-images">No images found for this session</div>'
        }
      })
      .catch((err) => {
        console.error("Error fetching images:", err)
        imagesContainer.innerHTML = '<div class="no-images">Error loading images</div>'
      })
  }

  // Hide the gallery and return to the camera view
  function hideGallery() {
    galleryContainer.classList.add("hidden")
    appContainer.classList.remove("hidden")
  }

  // Reset the session for a new user
  function resetSession() {
    // Redirect to a new session
    window.location.href = "/capture?new=true"
  }

  // Download all images as a zip
  function downloadAllImages() {
    window.location.href = `/download_images?code=${sessionCode}`
  }

  // Initialize the app
  init()
})
