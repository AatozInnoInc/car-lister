using System.Text.Json;
using car_lister.Models;
using Microsoft.JSInterop;

namespace car_lister.Services
{
    public class CarService : BaseFirestoreService
    {
        public CarService(IJSRuntime jsRuntime) : base(jsRuntime)
        {
        }

        // Client Inventory methods
        public async Task<List<ScrapedCar>> GetClientInventoryAsync(string clientId)
        {
            try
            {
                var carsJson = await _jsRuntime.InvokeAsync<string>("firestore.getClientInventory", clientId);
                if (string.IsNullOrEmpty(carsJson) || carsJson == "[]")
                {
                    return new List<ScrapedCar>();
                }

                var cars = JsonSerializer.Deserialize<List<ScrapedCar>>(carsJson, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                return cars ?? new List<ScrapedCar>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting client inventory: {ex.Message}");
                return new List<ScrapedCar>();
            }
        }

        public async Task<bool> AddToClientInventoryAsync(string clientId, ScrapedCar car)
        {
            if (string.IsNullOrEmpty(car.Id))
            {
                car.Id = Guid.NewGuid().ToString();
            }
            
            car.ScrapedAt = DateTime.UtcNow;
            car.ClientId = clientId; // Ensure the clientId is set

            return await _jsRuntime.InvokeAsync<bool>("firestore.addToClientInventory", clientId, JsonSerializer.Serialize(car));
        }

        public async Task<bool> AddMultipleToClientInventoryAsync(string clientId, List<ScrapedCar> cars)
        {
            // Ensure all cars have IDs, timestamps, and clientId
            foreach (var car in cars)
            {
                if (string.IsNullOrEmpty(car.Id))
                {
                    car.Id = Guid.NewGuid().ToString();
                }
                car.ScrapedAt = DateTime.UtcNow;
                car.ClientId = clientId; // Ensure the clientId is set
            }

            return await _jsRuntime.InvokeAsync<bool>("firestore.addMultipleToClientInventory", clientId, JsonSerializer.Serialize(cars));
        }

        public async Task<bool> UpdateClientInventoryCarAsync(string clientId, ScrapedCar car)
        {
            car.ScrapedAt = DateTime.UtcNow;
            car.ClientId = clientId; // Ensure the clientId is set

            return await _jsRuntime.InvokeAsync<bool>("firestore.updateClientInventoryCar", clientId, JsonSerializer.Serialize(car));
        }

        public async Task<bool> DeleteFromClientInventoryAsync(string clientId, string carId)
        {
            return await _jsRuntime.InvokeAsync<bool>("firestore.deleteFromClientInventory", clientId, carId);
        }

        public async Task<bool> ClearClientInventoryAsync(string clientId)
        {
            return await _jsRuntime.InvokeAsync<bool>("firestore.clearClientInventory", clientId);
        }
    }
}
