using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using Microsoft.AspNetCore.Components.Authorization;
using car_lister;
using car_lister.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
builder.Services.AddScoped<FirebaseService>();
builder.Services.AddScoped<DealerService>();
builder.Services.AddScoped<ClientService>();
builder.Services.AddScoped<AuthenticationStateProvider, FirebaseAuthenticationStateProvider>();
builder.Services.AddScoped<FirebaseAuthService>();
builder.Services.AddAuthorizationCore();

await builder.Build().RunAsync();
