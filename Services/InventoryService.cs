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
		return _navigationManager.BaseUri.Contains("localhost") 
				? "http://localhost:8000" 
				: "https://car-lister-api.onrender.com";
	}

	public async Task<InventorySearchResult> SearchDealerInventoryAsync(InventorySearchRequest request)
	{
		try
		{
				var baseUrl = GetBaseUrl();
				_httpClient.BaseAddress = new Uri(baseUrl);
				_httpClient.DefaultRequestHeaders.Clear();
				_httpClient.DefaultRequestHeaders.Add("Accept", "application/json");

				var response = await _httpClient.PostAsJsonAsync("/api/dealer/inventory", request);
				
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

	public async Task<bool> SaveCarsToFirestoreAsync(List<ScrapedCar> cars)
	{
		return await _carService.AddCarsAsync(cars);
	}

	public async Task<List<ScrapedCar>> GetCarsByClientIdAsync(string clientId)
	{
		return await _carService.GetCarsByClientIdAsync(clientId);
	}

	public async Task<bool> DeleteCarsByClientIdAsync(string clientId)
	{
		return await _carService.DeleteCarsByClientIdAsync(clientId);
	}
}