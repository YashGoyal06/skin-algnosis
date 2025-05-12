// Custom cursor effect
document.addEventListener('DOMContentLoaded', function() {
    // Create cursor glow element
    const cursorGlow = document.createElement('div');
    cursorGlow.classList.add('cursor-glow');
    document.body.appendChild(cursorGlow);
    
    // Variables for storing mouse position
    let mouseX = 0;
    let mouseY = 0;
    
    // Update mouse position on mouse move
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Show the cursor glow and position it at the mouse coordinates
        cursorGlow.style.opacity = '1';
        cursorGlow.style.left = mouseX + 'px';
        cursorGlow.style.top = mouseY + 'px';
    });
    
    // Increase cursor glow size when hovering clickable elements
    const clickableElements = document.querySelectorAll('a, button, input[type="submit"], .cta-button, .submit-button, .feature-card, .testimonial-card, .step-number, nav ul li a, .footer-links ul li a, input[type="checkbox"], input[type="radio"], select, .color-label, .checkbox-option');
    
    clickableElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            cursorGlow.style.width = '60px';
            cursorGlow.style.height = '60px';
            cursorGlow.style.background = 'radial-gradient(circle, rgba(255, 143, 48, 0.4) 0%, rgba(255, 143, 48, 0) 70%)';
        });
        
        element.addEventListener('mouseleave', function() {
            cursorGlow.style.width = '40px';
            cursorGlow.style.height = '40px';
            cursorGlow.style.background = 'radial-gradient(circle, rgba(55, 199, 255, 0.4) 0%, rgba(55, 199, 255, 0) 70%)';
        });
    });
    
    // Hide cursor glow when mouse leaves the window
    document.addEventListener('mouseout', function(e) {
        if (e.relatedTarget === null) {
            cursorGlow.style.opacity = '0';
        }
    });
    
    // Show cursor glow when mouse enters the window
    document.addEventListener('mouseover', function() {
        cursorGlow.style.opacity = '1';
    });
    
    // Add cursor click effect
    document.addEventListener('mousedown', function() {
        cursorGlow.style.transform = 'translate(-50%, -50%) scale(0.9)';
    });
    
    document.addEventListener('mouseup', function() {
        cursorGlow.style.transform = 'translate(-50%, -50%) scale(1)';
    });
});