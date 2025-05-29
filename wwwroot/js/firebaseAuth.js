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
            const result = await firebase.auth().signInWithPopup(provider);
            return !!result.user;
        } catch (error) {
            console.error("Error signing in with Google:", error);
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
    }
}; 