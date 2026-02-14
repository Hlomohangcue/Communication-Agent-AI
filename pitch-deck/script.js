// Pitch Deck Navigation Script

let currentSlide = 1;
const totalSlides = 15;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateSlideDisplay();
    setupEventListeners();
    setupKeyboardNavigation();
});

// Setup Event Listeners
function setupEventListeners() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    prevBtn.addEventListener('click', () => navigateSlide(-1));
    nextBtn.addEventListener('click', () => navigateSlide(1));
}

// Setup Keyboard Navigation
function setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            navigateSlide(-1);
        } else if (e.key === 'ArrowRight' || e.key === ' ') {
            e.preventDefault();
            navigateSlide(1);
        } else if (e.key === 'Home') {
            goToSlide(1);
        } else if (e.key === 'End') {
            goToSlide(totalSlides);
        }
    });
}

// Navigate Slide
function navigateSlide(direction) {
    const newSlide = currentSlide + direction;
    
    if (newSlide >= 1 && newSlide <= totalSlides) {
        currentSlide = newSlide;
        updateSlideDisplay();
    }
}

// Go to Specific Slide
function goToSlide(slideNumber) {
    if (slideNumber >= 1 && slideNumber <= totalSlides) {
        currentSlide = slideNumber;
        updateSlideDisplay();
    }
}

// Update Slide Display
function updateSlideDisplay() {
    // Hide all slides
    const slides = document.querySelectorAll('.slide');
    slides.forEach(slide => {
        slide.classList.remove('active');
    });

    // Show current slide
    const currentSlideElement = document.getElementById(`slide-${currentSlide}`);
    if (currentSlideElement) {
        currentSlideElement.classList.add('active');
    }

    // Update counter
    const counter = document.getElementById('slide-counter');
    counter.textContent = `${currentSlide} / ${totalSlides}`;

    // Update button states
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    prevBtn.disabled = currentSlide === 1;
    nextBtn.disabled = currentSlide === totalSlides;

    // Scroll to top of slide content
    const slideContent = currentSlideElement.querySelector('.slide-content');
    if (slideContent) {
        slideContent.scrollTop = 0;
    }
}

// Touch/Swipe Support for Mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - next slide
            navigateSlide(1);
        } else {
            // Swipe right - previous slide
            navigateSlide(-1);
        }
    }
}

// Fullscreen Toggle (F key)
document.addEventListener('keydown', (e) => {
    if (e.key === 'f' || e.key === 'F') {
        toggleFullscreen();
    }
});

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Print Mode (P key)
document.addEventListener('keydown', (e) => {
    if (e.key === 'p' || e.key === 'P') {
        e.preventDefault();
        window.print();
    }
});

// Slide Overview Mode (O key)
let overviewMode = false;

document.addEventListener('keydown', (e) => {
    if (e.key === 'o' || e.key === 'O') {
        toggleOverviewMode();
    }
});

function toggleOverviewMode() {
    overviewMode = !overviewMode;
    const presentation = document.querySelector('.presentation');
    
    if (overviewMode) {
        presentation.classList.add('overview-mode');
        showAllSlides();
    } else {
        presentation.classList.remove('overview-mode');
        updateSlideDisplay();
    }
}

function showAllSlides() {
    const slides = document.querySelectorAll('.slide');
    slides.forEach((slide, index) => {
        slide.classList.add('active');
        slide.style.position = 'relative';
        slide.style.display = 'block';
        slide.style.opacity = '1';
        slide.style.marginBottom = '20px';
    });
}

// Auto-advance Timer (optional)
let autoAdvanceTimer = null;
let autoAdvanceEnabled = false;

function startAutoAdvance(intervalSeconds = 10) {
    if (autoAdvanceTimer) {
        clearInterval(autoAdvanceTimer);
    }

    autoAdvanceEnabled = true;
    autoAdvanceTimer = setInterval(() => {
        if (currentSlide < totalSlides) {
            navigateSlide(1);
        } else {
            stopAutoAdvance();
        }
    }, intervalSeconds * 1000);
}

function stopAutoAdvance() {
    if (autoAdvanceTimer) {
        clearInterval(autoAdvanceTimer);
        autoAdvanceTimer = null;
    }
    autoAdvanceEnabled = false;
}

// Toggle auto-advance with 'A' key
document.addEventListener('keydown', (e) => {
    if (e.key === 'a' || e.key === 'A') {
        if (autoAdvanceEnabled) {
            stopAutoAdvance();
            console.log('Auto-advance stopped');
        } else {
            startAutoAdvance(10);
            console.log('Auto-advance started (10 seconds per slide)');
        }
    }
});

// Help Menu (H key)
document.addEventListener('keydown', (e) => {
    if (e.key === 'h' || e.key === 'H') {
        showHelpMenu();
    }
});

function showHelpMenu() {
    const helpText = `
KEYBOARD SHORTCUTS:
→ or Space: Next slide
← : Previous slide
Home: First slide
End: Last slide
F: Toggle fullscreen
P: Print presentation
O: Overview mode (all slides)
A: Auto-advance toggle
H: Show this help menu
ESC: Exit fullscreen/overview

MOUSE/TOUCH:
Click buttons to navigate
Swipe left/right on mobile
    `;
    
    alert(helpText);
}

// Presentation Timer
let presentationStartTime = null;
let timerInterval = null;

function startPresentationTimer() {
    presentationStartTime = Date.now();
    
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - presentationStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        console.log(`Presentation time: ${minutes}:${seconds.toString().padStart(2, '0')}`);
    }, 1000);
}

function stopPresentationTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// Start timer when first slide is shown
if (currentSlide === 1) {
    startPresentationTimer();
}

// Analytics (track slide views)
const slideViews = {};

function trackSlideView(slideNumber) {
    if (!slideViews[slideNumber]) {
        slideViews[slideNumber] = 0;
    }
    slideViews[slideNumber]++;
    
    // Log to console (can be sent to analytics service)
    console.log(`Slide ${slideNumber} viewed ${slideViews[slideNumber]} time(s)`);
}

// Track current slide view
trackSlideView(currentSlide);

// Update tracking on slide change
const originalNavigateSlide = navigateSlide;
navigateSlide = function(direction) {
    originalNavigateSlide(direction);
    trackSlideView(currentSlide);
};

// Smooth scroll for slide content
document.querySelectorAll('.slide-content').forEach(content => {
    content.style.scrollBehavior = 'smooth';
});

// Prevent accidental navigation away
window.addEventListener('beforeunload', (e) => {
    if (currentSlide > 1 && currentSlide < totalSlides) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Console welcome message
console.log('%c Communication Bridge AI - Pitch Deck ', 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 20px; padding: 10px;');
console.log('Press H for keyboard shortcuts');
console.log('Total slides:', totalSlides);

// Export functions for external use
window.pitchDeck = {
    goToSlide,
    navigateSlide,
    startAutoAdvance,
    stopAutoAdvance,
    toggleFullscreen,
    toggleOverviewMode,
    getCurrentSlide: () => currentSlide,
    getTotalSlides: () => totalSlides,
    getSlideViews: () => slideViews
};
