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
}