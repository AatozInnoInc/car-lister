window.firebaseAuth = {
    ensureInitialized: function() {
        if (!window.firebaseInitialized) {
            throw new Error('Firebase has not been initialized yet');
        }
    },

    signInWithGoogle: async function () {
        try {
            this.ensureInitialized();
            const provider = new firebase.auth.GoogleAuthProvider();
            
            // Set the redirect URL explicitly for localhost
            const currentHost = window.location.hostname;
            const isLocalhost = currentHost === 'localhost' || currentHost === '127.0.0.1';
            
            if (isLocalhost) {
                // For localhost, we need to handle the redirect manually
                try {
                    const result = await firebase.auth().signInWithPopup(provider);
                    return !!result.user;
                } catch (popupError) {
                    // Fallback to redirect if popup fails
                    await firebase.auth().signInWithRedirect(provider);
                    return true;
                }
            } else {
                // Use redirect for production
                await firebase.auth().signInWithRedirect(provider);
                return true;
            }
        } catch (error) {
            console.error("Error signing in with Google:", error);
            return false;
        }
    },

    handleRedirectResult: async function () {
        try {
            this.ensureInitialized();
            const result = await firebase.auth().getRedirectResult();
            return !!result.user;
        } catch (error) {
            console.error("Error handling redirect result:", error);
            return false;
        }
    },

    signOut: async function () {
        try {
            this.ensureInitialized();
            await firebase.auth().signOut();
            return true;
        } catch (error) {
            console.error("Error signing out:", error);
            return false;
        }
    },

    isUserAuthenticated: async function () {
        try {
            this.ensureInitialized();
            return new Promise((resolve) => {
                const unsubscribe = firebase.auth().onAuthStateChanged((user) => {
                    unsubscribe(); // Unsubscribe after first check
                    resolve(!!user);
                });
            });
        } catch (error) {
            console.error("Error checking authentication:", error);
            return false;
        }
    },

    getCurrentUser: function() {
        try {
            this.ensureInitialized();
            const user = firebase.auth().currentUser;
            if (!user) return null;
            
            return {
                uid: user.uid,
                email: user.email,
                displayName: user.displayName,
                photoURL: user.photoURL
            };
        } catch (error) {
            console.error("Error getting current user:", error);
            return null;
        }
    },

    onAuthStateChanged: function(callback) {
        try {
            this.ensureInitialized();
            return firebase.auth().onAuthStateChanged(callback);
        } catch (error) {
            console.error("Error setting up auth state listener:", error);
            return null;
        }
    }
};

// Download functionality
window.downloadFile = function(fileName, content) {
    try {
        const blob = new Blob([content], { type: 'text/html' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error("Error downloading file:", error);
        throw error;
    }
};

// Focus element for keyboard navigation
window.focusElement = function(elementId) {
    try {
        const element = document.getElementById(elementId);
        if (element) {
            element.focus();
        }
    } catch (error) {
        console.error("Error focusing element:", error);
    }
};

// Download images directly
window.downloadImages = async function(imageUrls, fileName, carTitle) {
    try {
        // Create a zip file using JSZip
        const JSZip = window.JSZip;
        if (!JSZip) {
            throw new Error('JSZip library not loaded. Please include JSZip in your project.');
        }

        const zip = new JSZip();
        
        // Download each image and add to zip
        for (let i = 0; i < imageUrls.length; i++) {
            try {
                const response = await fetch(imageUrls[i]);
                if (!response.ok) {
                    console.warn(`Failed to download image ${i + 1}: ${imageUrls[i]}`);
                    continue;
                }
                
                const blob = await response.blob();
                const imageExtension = getImageExtension(imageUrls[i]);
                const imageName = `${carTitle.replace(/[^a-zA-Z0-9]/g, '_')}_image_${i + 1}${imageExtension}`;
                
                zip.file(imageName, blob);
            } catch (error) {
                console.warn(`Error downloading image ${i + 1}:`, error);
            }
        }

        // Generate and download the zip file
        const zipBlob = await zip.generateAsync({ type: 'blob' });
        const url = window.URL.createObjectURL(zipBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error("Error downloading images:", error);
        throw error;
    }
};

// Helper function to get image extension from URL
function getImageExtension(url) {
    try {
        const urlObj = new URL(url);
        const pathname = urlObj.pathname;
        const extension = pathname.split('.').pop().toLowerCase();
        
        // Map common image extensions
        const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
        if (imageExtensions.includes(extension)) {
            return '.' + extension;
        }
        
        // Default to .jpg if no valid extension found
        return '.jpg';
    } catch (error) {
        return '.jpg';
    }
} 