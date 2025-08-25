using Microsoft.JSInterop;
using System.Threading.Tasks;

namespace car_lister.Services;

public class FirebaseUser
{
    public string Uid { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string PhotoURL { get; set; } = string.Empty;
}

public class FirebaseService
{
    private readonly IJSRuntime _jsRuntime;

    public FirebaseService(IJSRuntime jsRuntime)
    {
        _jsRuntime = jsRuntime;
    }

    // Google OAuth Authentication
    public async Task<bool> SignInWithGoogle()
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("firebaseAuth.signInWithGoogle");
        }
        catch
        {
            return false;
        }
    }

    // Handle redirect result after authentication
    public async Task<bool> HandleRedirectResult()
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("firebaseAuth.handleRedirectResult");
        }
        catch
        {
            return false;
        }
    }

    public async Task SignOut()
    {
        await _jsRuntime.InvokeVoidAsync("firebaseAuth.signOut");
    }

    public async Task<bool> IsUserAuthenticated()
    {
        return await _jsRuntime.InvokeAsync<bool>("firebaseAuth.isUserAuthenticated");
    }

    public async Task<FirebaseUser?> GetCurrentUser()
    {
        try
        {
            return await _jsRuntime.InvokeAsync<FirebaseUser>("firebaseAuth.getCurrentUser");
        }
        catch
        {
            return null;
        }
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
        await _jsRuntime.InvokeVoidAsync("firebase.database().ref", path);
        await _jsRuntime.InvokeVoidAsync("set", value);
    }

    // Example: Get data from the database
    public async Task<T> GetDatabaseValue<T>(string path)
    {
        var snapshot = await _jsRuntime.InvokeAsync<object>("firebase.database().ref", path);
        await _jsRuntime.InvokeAsync<object>("once", "value");
        // You'll need to handle deserialization of the snapshot value
        return default; // Placeholder
    }
}