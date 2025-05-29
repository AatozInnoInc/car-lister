window.firebaseAuth = {
    signInWithGoogle: async function () {
        try {
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
            await firebase.auth().signOut();
            return true;
        } catch (error) {
            console.error("Error signing out:", error);
            return false;
        }
    },

    isUserAuthenticated: async function () {
        return new Promise((resolve) => {
            const unsubscribe = firebase.auth().onAuthStateChanged((user) => {
                unsubscribe(); // Unsubscribe after first check
                resolve(!!user);
            });
        });
    },

    getCurrentUser: function() {
        const user = firebase.auth().currentUser;
        if (!user) return null;
        
        return {
            uid: user.uid,
            email: user.email,
            displayName: user.displayName,
            photoURL: user.photoURL
        };
    }
}; 