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

        public async Task<List<ScrapedCar>> GetCarsByClientIdAsync(string clientId)
        {
            try
            {
                var carsJson = await _jsRuntime.InvokeAsync<string>("firestore.getCarsByClientId", clientId);
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
                Console.WriteLine($"Error getting cars by client ID: {ex.Message}");
                return new List<ScrapedCar>();
            }
        }

        public async Task<List<Car>> GetLegacyCarsByClientIdAsync(string clientId)
        {
            try
            {
                var carsJson = await _jsRuntime.InvokeAsync<string>("firestore.getCarsByClientId", clientId);
                if (string.IsNullOrEmpty(carsJson) || carsJson == "[]")
                {
                    return new List<Car>();
                }

                var cars = JsonSerializer.Deserialize<List<Car>>(carsJson, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                return cars ?? new List<Car>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting legacy cars by client ID: {ex.Message}");
                return new List<Car>();
            }
        }

        public async Task<bool> AddCarAsync(ScrapedCar car)
        {
            if (string.IsNullOrEmpty(car.Id))
            {
                car.Id = Guid.NewGuid().ToString();
            }
            
            car.ScrapedAt = DateTime.UtcNow;

            return await AddAsync(car, "addCar");
        }

        public async Task<bool> AddCarsAsync(List<ScrapedCar> cars)
        {
            // Ensure all cars have IDs and timestamps
            foreach (var car in cars)
            {
                if (string.IsNullOrEmpty(car.Id))
                {
                    car.Id = Guid.NewGuid().ToString();
                }
                car.ScrapedAt = DateTime.UtcNow;
            }

            return await AddAsync(cars, "addCars");
        }

        public async Task<bool> AddLegacyCarsAsync(List<Car> cars)
        {
            // Ensure all cars have IDs and timestamps
            foreach (var car in cars)
            {
                if (string.IsNullOrEmpty(car.Id))
                {
                    car.Id = Guid.NewGuid().ToString();
                }
                car.CreatedAt = DateTime.UtcNow;
                car.LastUpdated = DateTime.UtcNow;
            }

            return await AddAsync(cars, "addCars");
        }

        public async Task<bool> UpdateCarAsync(ScrapedCar car)
        {
            car.ScrapedAt = DateTime.UtcNow;
            return await UpdateAsync(car, "updateCar");
        }

        public async Task<bool> UpdateLegacyCarAsync(Car car)
        {
            car.LastUpdated = DateTime.UtcNow;
            return await UpdateAsync(car, "updateCar");
        }

        public async Task<bool> DeleteCarAsync(string id)
        {
            return await DeleteAsync(id, "deleteCar");
        }

        public async Task<bool> DeleteCarsByClientIdAsync(string clientId)
        {
            return await DeleteByClientIdAsync(clientId, "deleteCarsByClientId");
        }
    }
}
