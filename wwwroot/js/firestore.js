window.firestore = {
    getUserTodos: async function(userId) {
        try {
            // First try with ordering (using index)
            try {
                const snapshot = await db.collection('todos')
                    .where('userId', '==', userId)
                    .orderBy('createdAt', 'desc')
                    .get();

                return snapshot.docs.map(doc => ({
                    id: doc.id,
                    ...doc.data(),
                    createdAt: doc.data().createdAt?.toDate().toISOString(),
                    completedAt: doc.data().completedAt?.toDate()?.toISOString()
                }));
            } catch (indexError) {
                // If index is not ready, fall back to simple query
                console.log("Index not ready, falling back to simple query");
                const snapshot = await db.collection('todos')
                    .where('userId', '==', userId)
                    .get();

                // Sort in memory instead
                return snapshot.docs
                    .map(doc => ({
                        id: doc.id,
                        ...doc.data(),
                        createdAt: doc.data().createdAt?.toDate().toISOString(),
                        completedAt: doc.data().completedAt?.toDate()?.toISOString()
                    }))
                    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
            }
        } catch (error) {
            console.error('Error getting todos:', error);
            throw error;
        }
    },

    addTodo: async function(todo) {
        try {
            const docRef = await db.collection('todos').add({
                userId: todo.userId,
                title: todo.title,
                description: todo.description,
                isCompleted: todo.isCompleted,
                createdAt: firebase.firestore.Timestamp.fromDate(new Date(todo.createdAt)),
                completedAt: todo.completedAt ? firebase.firestore.Timestamp.fromDate(new Date(todo.completedAt)) : null
            });
            return docRef.id;
        } catch (error) {
            console.error('Error adding todo:', error);
            throw error;
        }
    },

    updateTodo: async function(todo) {
        try {
            await db.collection('todos').doc(todo.id).update({
                title: todo.title,
                description: todo.description,
                isCompleted: todo.isCompleted,
                completedAt: todo.completedAt ? firebase.firestore.Timestamp.fromDate(new Date(todo.completedAt)) : null
            });
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
    }
}; 