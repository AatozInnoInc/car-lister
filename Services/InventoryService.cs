using System.Net.Http.Json;
using System.Text.Json;
using car_lister.Models;
using Microsoft.AspNetCore.Components;

namespace car_lister.Services;

public class InventoryService
{
    private readonly HttpClient _httpClient;
    private readonly NavigationManager _navigationManager;
    private readonly CarService _carService;

    public InventoryService(HttpClient httpClient, NavigationManager navigationManager, CarService carService)
    {
        _httpClient = httpClient;
        _navigationManager = navigationManager;
        _carService = carService;
    }

    private string GetBaseUrl()
    {
        var baseUri = _navigationManager.BaseUri ?? string.Empty;
        return (baseUri.Contains("localhost") || baseUri.Contains("127.0.0.1"))
                ? "http://localhost:8000"
                : "https://car-lister-api.onrender.com";
    }

    public async Task<InventorySearchResult> SearchDealerInventoryAsync(InventorySearchRequest request)
    {
        try
        {
            var baseUrl = GetBaseUrl();
            var response = await _httpClient.PostAsJsonAsync($"{baseUrl}/api/dealer/inventory", request);

            if (response.IsSuccessStatusCode)
            {
                var jsonString = await response.Content.ReadAsStringAsync();
                var result = JsonSerializer.Deserialize<InventorySearchResult>(jsonString, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                // Hydrate cars with full image lists via VDP scrape when tiles only have a primary image
                if (result?.Cars != null && result.Cars.Count > 0)
                    await HydrateCarsWithVdpImagesAsync(result.Cars);

                return result ?? new InventorySearchResult
                {
                    Success = false,
                    ErrorMessage = "Failed to deserialize response"
                };
            }
            else
            {
                return new InventorySearchResult
                {
                    Success = false,
                    ErrorMessage = $"Search failed with status code: {response.StatusCode}"
                };
            }
        }
        catch (Exception ex)
        {
            return new InventorySearchResult
            {
                Success = false,
                ErrorMessage = $"Error searching inventory: {ex.Message}"
            };
        }
    }

    public async Task<InventorySearchResult> SearchDealerInventoryAsync(
        string dealerEntityId,
        string dealerName,
        string dealerUrl,
        int pageNumber = 1,
        string inventoryType = "ALL")
    {
        var request = new InventorySearchRequest
        {
            DealerEntityId = dealerEntityId,
            DealerName = dealerName,
            DealerUrl = dealerUrl,
            PageNumber = pageNumber,
            InventoryType = inventoryType
        };

        return await SearchDealerInventoryAsync(request);
    }

    // Client inventory methods
    public async Task<bool> SaveCarsToClientInventoryAsync(string clientId, List<ScrapedCar> cars)
    {
        return await _carService.AddMultipleToClientInventoryAsync(clientId, cars);
    }

    public async Task<List<ScrapedCar>> GetClientInventoryAsync(string clientId)
    {
        return await _carService.GetClientInventoryAsync(clientId);
    }

    public async Task<bool> ClearClientInventoryAsync(string clientId)
    {
        return await _carService.ClearClientInventoryAsync(clientId);
    }

    public async Task<bool> AddCarToClientInventoryAsync(string clientId, ScrapedCar car)
    {
        return await _carService.AddToClientInventoryAsync(clientId, car);
    }

    public async Task<bool> UpdateCarInClientInventoryAsync(string clientId, ScrapedCar car)
    {
        return await _carService.UpdateClientInventoryCarAsync(clientId, car);
    }

    public async Task<bool> DeleteCarFromClientInventoryAsync(string clientId, string carId)
    {
        return await _carService.DeleteFromClientInventoryAsync(clientId, carId);
    }

    // Scrape a single listing by URL (VDP) to hydrate images when needed
    public async Task<ScrapedCar?> ScrapeCarByUrlAsync(string url)
    {
        try
        {
            var baseUrl = GetBaseUrl();
            var payload = new { url };
            var response = await _httpClient.PostAsJsonAsync($"{baseUrl}/api/scrape", payload);
            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"Hydration: /api/scrape failed: {(int)response.StatusCode} {response.StatusCode}");
                return null;
            }

            var jsonString = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(jsonString);
            var root = doc.RootElement;
            if (root.TryGetProperty("success", out var successEl) && successEl.GetBoolean() && root.TryGetProperty("data", out var dataEl))
            {
                var car = JsonSerializer.Deserialize<ScrapedCar>(dataEl.GetRawText(), new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                return car;
            }

            return null;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Hydration: /api/scrape exception: {ex.Message}");
            return null;
        }
    }

    private async Task HydrateCarsWithVdpImagesAsync(List<ScrapedCar> cars)
    {
        foreach (var car in cars)
        {
            try
            {
                if (car.Images != null && car.Images.Count > 1)
                {
                    continue;
                }
                var url = string.IsNullOrWhiteSpace(car.OriginalUrl) ? car.ListingUrl : car.OriginalUrl;
                if (string.IsNullOrWhiteSpace(url))
                {
                    continue;
                }
                var hydrated = await ScrapeCarByUrlAsync(url);
                if (hydrated?.Images != null && hydrated.Images.Count > (car.Images?.Count ?? 0))
                {
                    car.Images = hydrated.Images;
                    if (string.IsNullOrWhiteSpace(car.FullTitle) && !string.IsNullOrWhiteSpace(hydrated.FullTitle))
                    {
                        car.FullTitle = hydrated.FullTitle;
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Hydration: error for '{car.FullTitle}': {ex.Message}");
            }
        }
    }
}