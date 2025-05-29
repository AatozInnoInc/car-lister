window.firestore = {
    getUserTodos: async function(userId) {
        try {
            // First try with ordering (using index)
            try {
                const snapshot = await db.collection('todos')
                    .where('userId', '==', userId)
                    .orderBy('createdAt', 'desc')
                    .get();

                return snapshot.docs.map(doc => {
                    const data = doc.data();
                    // Convert Firestore timestamps to local datetime strings
                    const convertToLocal = (timestamp) => {
                        if (!timestamp) return null;
                        const date = timestamp.toDate();
                        return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString();
                    };

                    return {
                        id: doc.id,
                        ...data,
                        createdAt: convertToLocal(data.createdAt),
                        completedAt: convertToLocal(data.completedAt),
                        reminderDateTime: convertToLocal(data.reminderDateTime)
                    };
                });
            } catch (indexError) {
                // If index is not ready, fall back to simple query
                console.log("Index not ready, falling back to simple query");
                const snapshot = await db.collection('todos')
                    .where('userId', '==', userId)
                    .get();

                // Sort in memory instead
                return snapshot.docs
                    .map(doc => {
                        const data = doc.data();
                        // Convert Firestore timestamps to local datetime strings
                        const convertToLocal = (timestamp) => {
                            if (!timestamp) return null;
                            const date = timestamp.toDate();
                            return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString();
                        };

                        return {
                            id: doc.id,
                            ...data,
                            createdAt: convertToLocal(data.createdAt),
                            completedAt: convertToLocal(data.completedAt),
                            reminderDateTime: convertToLocal(data.reminderDateTime)
                        };
                    })
                    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
            }
        } catch (error) {
            console.error('Error getting todos:', error);
            throw error;
        }
    },

    addTodo: async function(todo) {
        try {
            console.log('Adding todo with raw data:', todo);
            
            // Convert local datetime strings to Firestore Timestamps
            const convertToTimestamp = (dateStr) => {
                if (!dateStr) return null;
                const date = new Date(dateStr);
                return firebase.firestore.Timestamp.fromDate(date);
            };
            
            const data = {
                userId: todo.userId,
                title: String(todo.title || ''),
                description: String(todo.description || ''),
                isCompleted: Boolean(todo.isCompleted),
                createdAt: firebase.firestore.Timestamp.now(),
                completedAt: null,
                reminderDateTime: convertToTimestamp(todo.reminderDateTime),
                reminderNote: String(todo.reminderNote || ''),
                isReminderAcknowledged: false
            };

            console.log('Sending to Firestore:', JSON.stringify(data, null, 2));
            
            // Validation
            if (!data.userId || typeof data.userId !== 'string') {
                throw new Error('userId must be a non-empty string');
            }
            if (typeof data.title !== 'string') {
                throw new Error('title must be a string');
            }
            if (typeof data.description !== 'string') {
                throw new Error('description must be a string');
            }
            if (typeof data.isCompleted !== 'boolean') {
                throw new Error('isCompleted must be a boolean');
            }

            const docRef = await db.collection('todos').add(data);
            console.log('Successfully added todo with ID:', docRef.id);
            return docRef.id;
        } catch (error) {
            console.error('Error adding todo:', error);
            throw error;
        }
    },

    updateTodo: async function(todo) {
        try {
            console.log('Updating todo:', todo);
            
            // Convert local datetime strings to Firestore Timestamps
            const convertToTimestamp = (dateStr) => {
                if (!dateStr) return null;
                const date = new Date(dateStr);
                return firebase.firestore.Timestamp.fromDate(date);
            };
            
            const data = {
                title: todo.title,
                description: todo.description,
                isCompleted: todo.isCompleted,
                completedAt: convertToTimestamp(todo.completedAt),
                reminderDateTime: convertToTimestamp(todo.reminderDateTime),
                reminderNote: todo.reminderNote || null,
                isReminderAcknowledged: todo.isReminderAcknowledged
            };

            console.log('Saving data:', data);
            await db.collection('todos').doc(todo.id).update(data);
            return true;
        } catch (error) {
            console.error('Error updating todo:', error);
            throw error;
        }
    },

    deleteTodo: async function(todoId) {
        try {
            await db.collection('todos').doc(todoId).delete();
            return true;
        } catch (error) {
            console.error('Error deleting todo:', error);
            throw error;
        }
    },

    getUpcomingReminders: async function(userId) {
        try {
            console.log('Getting upcoming reminders for user:', userId);
            
            // Get current time in user's timezone
            const now = new Date();
            const nowTimestamp = firebase.firestore.Timestamp.fromDate(now);
            
            console.log('Current local time:', now.toLocaleString());
            console.log('Current timestamp:', nowTimestamp);
            
            // Get todos with reminders that:
            // 1. Belong to the user
            // 2. Are not completed
            // 3. Have not been acknowledged
            // 4. Have a reminder time in the future (compared to local time)
            const snapshot = await db.collection('todos')
                .where('userId', '==', userId)
                .where('isCompleted', '==', false)
                .where('isReminderAcknowledged', '==', false)
                .where('reminderDateTime', '>', nowTimestamp)
                .orderBy('reminderDateTime', 'asc')
                .get();

            console.log('Found reminders:', snapshot.size);
            return snapshot.docs.map(doc => {
                const data = doc.data();
                console.log('Raw reminder data:', data);
                
                // Convert timestamps to local time
                const convertToLocal = (timestamp) => {
                    if (!timestamp) return null;
                    const date = timestamp.toDate();
                    return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString();
                };
                
                const reminderDateTime = convertToLocal(data.reminderDateTime);
                console.log('Converted reminder time:', reminderDateTime);
                
                return {
                    id: doc.id,
                    ...data,
                    createdAt: convertToLocal(data.createdAt),
                    completedAt: convertToLocal(data.completedAt),
                    reminderDateTime: reminderDateTime
                };
            });
        } catch (error) {
            console.error('Error getting upcoming reminders:', error);
            throw error;
        }
    }
}; 