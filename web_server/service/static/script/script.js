// Auto-dismiss flash messages after 5 seconds
setTimeout(function() {
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        message.style.display = 'none';
    });
}, 5000);

// Handle click events on flash messages
document.addEventListener('DOMContentLoaded', function() {
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        message.addEventListener('click', function() {
            this.style.display = 'none';
        });
    });

    // Prevent click on close button from triggering the message click event
    var closeButtons = document.querySelectorAll('.flash-message .close-btn');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            this.parentElement.style.display = 'none';
        });
    });
});