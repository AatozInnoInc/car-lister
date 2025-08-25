using Microsoft.AspNetCore.Components.Authorization;
using System.Security.Claims;

namespace car_lister.Services;

public class FirebaseAuthenticationStateProvider : AuthenticationStateProvider
{
    private readonly FirebaseService _firebaseService;

    public FirebaseAuthenticationStateProvider(FirebaseService firebaseService)
    {
        _firebaseService = firebaseService;
    }

    public override async Task<AuthenticationState> GetAuthenticationStateAsync()
    {
        try
        {
            // First, handle any pending redirect result
            var redirectResult = await _firebaseService.HandleRedirectResult();
            
            var isAuthenticated = await _firebaseService.IsUserAuthenticated();

            if (!isAuthenticated)
            {
                return new AuthenticationState(new ClaimsPrincipal(new ClaimsIdentity()));
            }

            // Get the current user from Firebase
            var user = await _firebaseService.GetCurrentUser();
            
            if (user == null)
            {
                return new AuthenticationState(new ClaimsPrincipal(new ClaimsIdentity()));
            }

            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.NameIdentifier, user.Uid),
                new Claim(ClaimTypes.Name, user.DisplayName ?? user.Email ?? "Firebase User"),
                new Claim(ClaimTypes.Email, user.Email ?? ""),
                new Claim(ClaimTypes.Role, "User")
            };

            if (!string.IsNullOrEmpty(user.PhotoURL))
            {
                claims.Add(new Claim("PhotoURL", user.PhotoURL));
            }

            var identity = new ClaimsIdentity(claims, "Firebase authentication");
            var principal = new ClaimsPrincipal(identity);
            
            return new AuthenticationState(principal);
        }
        catch (Exception ex)
        {
            // Log the error and return unauthenticated state
            Console.WriteLine($"Error in GetAuthenticationStateAsync: {ex.Message}");
            return new AuthenticationState(new ClaimsPrincipal(new ClaimsIdentity()));
        }
    }

    public void NotifyAuthenticationStateChanged()
    {
        NotifyAuthenticationStateChanged(GetAuthenticationStateAsync());
    }
} 