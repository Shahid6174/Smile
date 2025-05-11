document.addEventListener("DOMContentLoaded", () => {
  const sessionCodeInput = document.getElementById("session-code-input");
  const searchBtn = document.getElementById("search-btn");
  const galleryImages = document.getElementById("gallery-images");
  const downloadAllBtn = document.getElementById("download-all-gallery");

  function init() {
    searchBtn.addEventListener("click", searchImages);
    sessionCodeInput.addEventListener("keypress", function(event) {
      if (event.key === "Enter") {
        searchImages();
      }
    });
    downloadAllBtn.addEventListener("click", downloadAllImages);
  }
  function searchImages() {
    const sessionCode = sessionCodeInput.value.trim();
    
    if (!sessionCode || sessionCode.length !== 6) {

      showError("Please enter a valid 6-digit session code🙅");

      return;
    }
    galleryImages.innerHTML = '<div class="loading">Loading images...🤔</div>';

    downloadAllBtn.disabled = true;



    fetch(`/get_images_by_code?code=${sessionCode}`)
      .then(response => response.json())
      .then(data => {
        if (data.images && data.images.length > 0) {
          displayImages(data.images, sessionCode);
          downloadAllBtn.disabled = false;
        } else {
          showError("You Havent Captured Any smiles Yet😊");
        }
      })
      .catch(err => {
        console.error("Error fetching images:🥺", err);
        showError("Error loading images. Please try again.🙇");
      });
  }



  function displayImages(images, sessionCode) {

    galleryImages.innerHTML = "";
    
    images.forEach((image, index) => {
      const imageCard = document.createElement("div");
      imageCard.className = "image-card";

      imageCard.innerHTML = `
        <img src="/static/images/${sessionCode}/${image}" alt="Captured smile ${index + 1}">
        <div class="image-info">
          <p>Smile ${index + 1} of ${images.length}</p>
        </div>
      `;

      galleryImages.appendChild(imageCard);
    });
  }
  function showError(message) {
    galleryImages.innerHTML = `<div class="no-images">${message}</div>`;
    downloadAllBtn.disabled = true;
  }
  function downloadAllImages() {
    const sessionCode = sessionCodeInput.value.trim();
    if (sessionCode) {
      window.location.href = `/download_images?code=${sessionCode}`;
    }
  }
  init();
});
