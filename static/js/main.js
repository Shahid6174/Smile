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
  const totalRequiredFrames = 15 
  const totalImages = 6 

  function init() {
    updateCaptureProgress()

    startBtn.addEventListener("click", startCamera)

    showImagesBtn.addEventListener("click", showGallery)

    doneBtn.addEventListener("click", resetSession)

    backBtn.addEventListener("click", hideGallery)
    downloadAllBtn.addEventListener("click", downloadAllImages)

    checkForExistingImages()
  }
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

  function startCamera() {
    faceGuide.style.display = "block"
    smileIndicator.style.display = "block"
    startBtn.textContent = "Camera Active"
    startBtn.disabled = true
    statusMessage.textContent = "Position your face and smile naturally"

    //the camera is already running via Flask's video_feed
    //User directly starts the smile detection simulation
    //We need to Modify this Issue Later On
    startSmileDetection()
  }

  function startSmileDetection() {
    smileDetectionActive = true

    const simulateSmileDetection = () => {
      if (!smileDetectionActive) return

      if (capturedImages < totalImages) {

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

  function captureImage() {
    capturedImages++
    updateCaptureProgress()

    statusMessage.textContent = `Smile captured! (${capturedImages}/${totalImages})`

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

    if (capturedImages === 1) {
      showImagesBtn.disabled = false
    }

    if (capturedImages >= totalImages) {
      completeCapture()
    }
  }

  function updateCaptureProgress() {
    dots.forEach((dot, index) => {
      if (index < capturedImages) {
        dot.classList.add("active")
      } else {
        dot.classList.remove("active")
      }
    })
  }

  function completeCapture() {
    smileDetectionActive = false
    statusMessage.textContent = 'All smiles captured! Click "Show Captured Images"'
    smileIndicator.style.display = "none"
    faceGuide.style.display = "none"
    showImagesBtn.classList.add("pulse")
  }

  function showGallery() {
    appContainer.classList.add("hidden")
    galleryContainer.classList.remove("hidden")

    galleryContainer.classList.add("fade-in")

    imagesContainer.innerHTML = ""

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
  function hideGallery() {
    galleryContainer.classList.add("hidden")
    appContainer.classList.remove("hidden")
  }
  function resetSession() {
    window.location.href = "/capture?new=true"
  }

  function downloadAllImages() {
    window.location.href = `/download_images?code=${sessionCode}`
  }

  init()
})
