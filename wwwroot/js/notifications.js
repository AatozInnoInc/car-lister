// Car Lister Notifications Interface
// This file will be expanded as we implement notification functionality

window.notifications = {
    requestPermission: async function() {
        console.log('Requesting notification permission');
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return false;
    },
    
    showNotification: async function(title, options) {
        console.log('Showing notification:', title, options);
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, options);
        }
    }
};

// Utility functions for UI interactions
window.scrollToTop = function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
};

window.scrollToResults = function() {
    const resultsSection = document.querySelector('.results-section');
    if (resultsSection) {
        resultsSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    } else {
        // Fallback to scrolling to top if results section not found
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
};

window.focusElement = function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.focus();
    }
};
