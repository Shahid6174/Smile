document.addEventListener('DOMContentLoaded', () => {
  const face = document.getElementById('face');
  const animateBtn = document.getElementById('animate');
  const resetBtn = document.getElementById('reset');
  const colorButtons = document.querySelectorAll('.color-button');
  const messageEl = document.getElementById('message');
  const messages = [
    "Have a great day!",
    "Keep smiling!",
    "You're awesome!",
    "Stay positive!",
    "Spread happiness!"
  ];

  let isAnimating = false;
  let animationInterval;

  // Animate button click handler
  animateBtn.addEventListener('click', () => {
    if (isAnimating) return;

    isAnimating = true;
    messageEl.textContent = messages[Math.floor(Math.random() * messages.length)];

    // Add animated class to face
    face.classList.add('animated');
    
    // Bounce animation
    let bounceUp = true;
    let scale = 1.1;
    animationInterval = setInterval(() => {
      if (bounceUp) {
        scale += 0.01;
        if (scale >= 1.15) bounceUp = false;
      } else {
        scale -= 0.01;
        if (scale <= 1.05) bounceUp = true;
      }
      face.style.transform = `scale(${scale})`;
    }, 50);
  });

  // Reset button click handler
  resetBtn.addEventListener('click', () => {
    if (!isAnimating) return;

    clearInterval(animationInterval);
    isAnimating = false;
    messageEl.textContent = '';

    // Remove animated class
    face.classList.remove('animated');
    face.style.transform = '';
  });

  // Color change functionality
  colorButtons.forEach(button => {
    button.addEventListener('click', () => {
      face.style.backgroundColor = button.getAttribute('data-color');
    });
  });
  
  // Hover effect for color buttons
  colorButtons.forEach(button => {
    button.addEventListener('mouseover', () => {
      button.style.transform = 'scale(1.2)';
    });
    
    button.addEventListener('mouseout', () => {
      button.style.transform = '';
    });
  });
});
