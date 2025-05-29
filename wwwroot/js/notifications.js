window.notifications = {
    isInitialized: false,

    initialize() {
        if (this.isInitialized) return;
        
        // Check if browser supports notifications
        if (!("Notification" in window)) {
            console.error("This browser does not support desktop notifications");
            return;
        }

        this.isInitialized = true;
    },

    async requestPermission() {
        try {
            if (!this.isInitialized) {
                this.initialize();
            }

            if (!("Notification" in window)) {
                console.error("This browser does not support desktop notifications");
                return false;
            }

            const permission = await Notification.requestPermission();
            return permission === 'granted';
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            return false;
        }
    },

    async checkPermission() {
        if (!this.isInitialized) {
            this.initialize();
        }

        if (!("Notification" in window)) {
            return false;
        }

        return Notification.permission === 'granted';
    },

    async showNotification(title, options = {}) {
        try {
            if (!this.isInitialized) {
                this.initialize();
            }

            if (!("Notification" in window)) {
                console.error("This browser does not support desktop notifications");
                return false;
            }

            if (await this.checkPermission()) {
                const notification = new Notification(title, {
                    icon: '/icon-192.png',
                    badge: '/icon-192.png',
                    ...options
                });

                notification.onclick = function(event) {
                    event.preventDefault();
                    window.focus();
                    notification.close();
                };

                return true;
            }
            return false;
        } catch (error) {
            console.error('Error showing notification:', error);
            return false;
        }
    }
};

// Initialize notifications when the script loads
window.notifications.initialize(); 