using Microsoft.JSInterop;
using System.Threading.Tasks;

namespace myapp.Services
{
    public class FirebaseService
    {
        private readonly IJSRuntime _jsRuntime;

        public FirebaseService(IJSRuntime jsRuntime)
        {
            _jsRuntime = jsRuntime;
        }

        // Example: Sign in with email and password
        public async Task<string> SignInWithEmailPassword(string email, string password)
        {
            return await _jsRuntime.InvokeAsync<string>("firebase.auth().signInWithEmailAndPassword", email, password);
        }

        // Example: Sign up with email and password
        public async Task<string> SignUpWithEmailPassword(string email, string password)
        {
            return await _jsRuntime.InvokeAsync<string>("firebase.auth().createUserWithEmailAndPassword", email, password);
        }

        // Example: Send data to the database
        public async Task SetDatabaseValue(string path, object value)
        {
            await _jsRuntime.InvokeVoidAsync("firebase.database().ref", path).InvokeVoidAsync("set", value);
        }

        // Example: Get data from the database
        public async Task<T> GetDatabaseValue<T>(string path)
        {
            var snapshot = await _jsRuntime.InvokeAsync<object>("firebase.database().ref", path).InvokeAsync<object>("once", "value");
            // You'll need to handle deserialization of the snapshot value
            return default; // Placeholder
        }
    }
}
