// Car Lister Firestore Interface
// This file will be expanded as we implement car listing functionality

window.firestore = {
    // Dealer functions
    getAllDealers: async function() {
        try {
            const db = firebase.firestore();
            const snapshot = await db.collection('dealers').get();
            const dealers = [];
            snapshot.forEach(doc => {
                dealers.push({
                    id: doc.id,
                    ...doc.data()
                });
            });
            return JSON.stringify(dealers);
        } catch (error) {
            console.error('Error getting dealers:', error);
            return '[]';
        }
    },

    getDealerById: async function(id) {
        try {
            const db = firebase.firestore();
            const doc = await db.collection('dealers').doc(id).get();
            if (doc.exists) {
                return JSON.stringify({
                    id: doc.id,
                    ...doc.data()
                });
            }
            return null;
        } catch (error) {
            console.error('Error getting dealer by id:', error);
            return null;
        }
    },

    addDealer: async function(dealerJson) {
        try {
            const dealer = JSON.parse(dealerJson);
            const db = firebase.firestore();
            const docRef = await db.collection('dealers').add(dealer);
            return true;
        } catch (error) {
            console.error('Error adding dealer:', error);
            return false;
        }
    },

    updateDealer: async function(dealerJson) {
        try {
            const dealer = JSON.parse(dealerJson);
            const db = firebase.firestore();
            await db.collection('dealers').doc(dealer.id).update(dealer);
            return true;
        } catch (error) {
            console.error('Error updating dealer:', error);
            return false;
        }
    },

    deleteDealer: async function(id) {
        try {
            const db = firebase.firestore();
            await db.collection('dealers').doc(id).delete();
            return true;
        } catch (error) {
            console.error('Error deleting dealer:', error);
            return false;
        }
    },

    // Client functions
    getAllClients: async function() {
        try {
            const db = firebase.firestore();
            const snapshot = await db.collection('clients').get();
            const clients = [];
            snapshot.forEach(doc => {
                clients.push({
                    id: doc.id,
                    ...doc.data()
                });
            });
            return JSON.stringify(clients);
        } catch (error) {
            console.error('Error getting clients:', error);
            return '[]';
        }
    },

    getClientById: async function(id) {
        try {
            const db = firebase.firestore();
            const doc = await db.collection('clients').doc(id).get();
            if (doc.exists) {
                return JSON.stringify({
                    id: doc.id,
                    ...doc.data()
                });
            }
            return null;
        } catch (error) {
            console.error('Error getting client by id:', error);
            return null;
        }
    },

    addClient: async function(clientJson) {
        try {
            const client = JSON.parse(clientJson);
            const db = firebase.firestore();
            const docRef = await db.collection('clients').add(client);
            return docRef.id; // Return the document ID instead of just true
        } catch (error) {
            console.error('Error adding client:', error);
            return null;
        }
    },

    updateClient: async function(clientJson) {
        try {
            const client = JSON.parse(clientJson);
            const db = firebase.firestore();
            await db.collection('clients').doc(client.id).update(client);
            return true;
        } catch (error) {
            console.error('Error updating client:', error);
            return false;
        }
    },

    deleteClient: async function(id) {
        try {
            const db = firebase.firestore();
            await db.collection('clients').doc(id).delete();
            return true;
        } catch (error) {
            console.error('Error deleting client:', error);
            return false;
        }
    },

    // Client Inventory functions
    getClientInventory: async function(clientId) {
        try {
            const db = firebase.firestore();
            const snapshot = await db.collection('clients').doc(clientId).collection('inventory').get();
            const cars = [];
            snapshot.forEach(doc => {
                cars.push({
                    id: doc.id,
                    ...doc.data()
                });
            });
            return JSON.stringify(cars);
        } catch (error) {
            console.error('Error getting client inventory:', error);
            return '[]';
        }
    },

    addToClientInventory: async function(clientId, carJson) {
        try {
            const car = JSON.parse(carJson);
            const db = firebase.firestore();
            const docRef = await db.collection('clients').doc(clientId).collection('inventory').add(car);
            return true;
        } catch (error) {
            console.error('Error adding car to client inventory:', error);
            return false;
        }
    },

    addMultipleToClientInventory: async function(clientId, carsJson) {
        try {
            const cars = JSON.parse(carsJson);
            const db = firebase.firestore();
            const batch = db.batch();
            
            cars.forEach(car => {
                const docRef = db.collection('clients').doc(clientId).collection('inventory').doc();
                batch.set(docRef, car);
            });
            
            await batch.commit();
            return true;
        } catch (error) {
            console.error('Error adding cars to client inventory:', error);
            return false;
        }
    },

    updateClientInventoryCar: async function(clientId, carJson) {
        try {
            const car = JSON.parse(carJson);
            const db = firebase.firestore();
            await db.collection('clients').doc(clientId).collection('inventory').doc(car.id).update(car);
            return true;
        } catch (error) {
            console.error('Error updating car in client inventory:', error);
            return false;
        }
    },

    deleteFromClientInventory: async function(clientId, carId) {
        try {
            const db = firebase.firestore();
            await db.collection('clients').doc(clientId).collection('inventory').doc(carId).delete();
            return true;
        } catch (error) {
            console.error('Error deleting car from client inventory:', error);
            return false;
        }
    },

    clearClientInventory: async function(clientId) {
        try {
            const db = firebase.firestore();
            const snapshot = await db.collection('clients').doc(clientId).collection('inventory').get();
            const batch = db.batch();
            
            snapshot.forEach(doc => {
                batch.delete(doc.ref);
            });
            
            await batch.commit();
            return true;
        } catch (error) {
            console.error('Error clearing client inventory:', error);
            return false;
        }
    },

    // Car listing functions (placeholder for future use)
    getUserCars: async function(userId) {
        console.log('getUserCars called for user:', userId);
        return [];
    },
    
    addCar: async function(car) {
        console.log('addCar called with:', car);
        return null;
    },
    
    updateCar: async function(car) {
        console.log('updateCar called with:', car);
        return false;
    },
    
    deleteCar: async function(carId) {
        console.log('deleteCar called for:', carId);
        return false;
    },
    
    getAllCars: async function() {
        console.log('getAllCars called');
        return [];
    }
};

// Generic scroll to element utility (replaces both thumbnail functions)
window.scrollToElement = function(containerSelector, elementSelector, activeIndex) {
    const container = document.querySelector(containerSelector);
    const element = document.querySelector(`${elementSelector}:nth-child(${activeIndex + 1})`);
    
    if (container && element) {
        const containerWidth = container.offsetWidth;
        const targetLeft = element.offsetLeft;
        const targetWidth = element.offsetWidth;
        const scrollLeft = targetLeft - (containerWidth / 2) + (targetWidth / 2);
        
        container.scrollTo({
            left: Math.max(0, scrollLeft),
            behavior: 'smooth'
        });
    }
};

// Thumbnail carousel functionality (now uses generic function)
window.scrollToActiveThumbnail = function(activeIndex) {
    window.scrollToElement('.thumbnail-scroll', '.thumbnail-wrapper', activeIndex);
};

// Fullscreen thumbnail carousel functionality (now uses generic function)
window.scrollToActiveFullscreenThumbnail = function(activeIndex) {
    window.scrollToElement('.fullscreen-thumbnails', '.fullscreen-thumbnail', activeIndex);
};

// Click outside listener for dropdowns
window.addClickOutsideListener = function(elementId, dotNetRef) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const clickHandler = function(event) {
        if (!element.contains(event.target)) {
            dotNetRef.invokeMethodAsync('OnClickOutside');
        }
    };
    
    // Remove existing listener if any
    if (window.clickOutsideHandler) {
        document.removeEventListener('click', window.clickOutsideHandler);
    }
    
    window.clickOutsideHandler = clickHandler;
    document.addEventListener('click', clickHandler);
};

// Focus element utility
window.focusElement = function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.focus();
    }
};

// Scroll to results utility
window.scrollToResults = function() {
    const resultsSection = document.querySelector('.results-section');
    if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
};

// Scroll to highlighted option in dropdown
window.scrollToHighlightedOption = function(containerId, highlightedIndex) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const options = container.querySelectorAll('.dropdown-option');
    if (highlightedIndex >= 0 && highlightedIndex < options.length) {
        const optionHeight = options[0].offsetHeight;
        const containerScrollTop = container.scrollTop;
        const containerHeight = container.clientHeight;
        const targetScrollTop = highlightedIndex * optionHeight;
        const optionBottom = targetScrollTop + optionHeight;
        const containerBottom = containerScrollTop + containerHeight;
        
        // Only scroll if the option is outside the visible area
        if (targetScrollTop < containerScrollTop || optionBottom > containerBottom) {
            container.scrollTop = targetScrollTop;
        }
    }
};

// Fullscreen keyboard navigation
window.setupFullscreenKeyboard = function(dotNetRef, closeMethod, prevMethod, nextMethod) {
    // Remove any existing listeners
    if (window.fullscreenKeyHandler) {
        document.removeEventListener('keydown', window.fullscreenKeyHandler);
    }
    
    // Create new handler
    window.fullscreenKeyHandler = function(e) {
        const fullscreenOverlay = document.querySelector('.fullscreen-overlay');
        if (!fullscreenOverlay) return;
        
        switch(e.key) {
            case 'Escape':
                dotNetRef.invokeMethodAsync(closeMethod);
                break;
            case 'ArrowLeft':
                dotNetRef.invokeMethodAsync(prevMethod);
                break;
            case 'ArrowRight':
                dotNetRef.invokeMethodAsync(nextMethod);
                break;
        }
    };
    
    document.addEventListener('keydown', window.fullscreenKeyHandler);
};

// Cleanup function
window.cleanupFullscreenKeyboard = function() {
    if (window.fullscreenKeyHandler) {
        document.removeEventListener('keydown', window.fullscreenKeyHandler);
        window.fullscreenKeyHandler = null;
    }
}; 