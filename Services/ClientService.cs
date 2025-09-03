using Microsoft.JSInterop;
using car_lister.Models;
using System.Text.Json;

namespace car_lister.Services;

public class ClientService
{
    private readonly IJSRuntime _jsRuntime;

    public ClientService(IJSRuntime jsRuntime)
    {
        _jsRuntime = jsRuntime;
    }

    // Client operations
    public async Task<List<Client>> GetAllClientsAsync()
    {
        try
        {
            var clientsJson = await _jsRuntime.InvokeAsync<string>("firestore.getAllClients");
            if (string.IsNullOrEmpty(clientsJson) || clientsJson == "[]")
            {
                return new List<Client>();
            }

            var clients = JsonSerializer.Deserialize<List<Client>>(clientsJson, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            return clients ?? new List<Client>();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting clients: {ex.Message}");
            return new List<Client>();
        }
    }

    public async Task<Client?> GetClientByIdAsync(string id)
    {
        try
        {
            var clientJson = await _jsRuntime.InvokeAsync<string>("firestore.getClientById", id);
            if (string.IsNullOrEmpty(clientJson))
            {
                return null;
            }

            return JsonSerializer.Deserialize<Client>(clientJson, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting client by id: {ex.Message}");
            return null;
        }
    }

    public async Task<bool> AddClientAsync(Client client)
    {
        try
        {
            client.Id = Guid.NewGuid().ToString();
            client.CreatedAt = DateTime.UtcNow;
            client.UpdatedAt = DateTime.UtcNow;

            var clientJson = JsonSerializer.Serialize(client);
            return await _jsRuntime.InvokeAsync<bool>("firestore.addClient", clientJson);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error adding client: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> UpdateClientAsync(Client client)
    {
        try
        {
            client.UpdatedAt = DateTime.UtcNow;
            var clientJson = JsonSerializer.Serialize(client);
            return await _jsRuntime.InvokeAsync<bool>("firestore.updateClient", clientJson);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error updating client: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> DeleteClientAsync(string id)
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("firestore.deleteClient", id);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error deleting client: {ex.Message}");
            return false;
        }
    }

    // Car operations
    public async Task<List<Car>> GetCarsByClientIdAsync(string clientId)
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
            Console.WriteLine($"Error getting cars by client id: {ex.Message}");
            return new List<Car>();
        }
    }

    public async Task<bool> AddCarAsync(Car car)
    {
        try
        {
            car.Id = Guid.NewGuid().ToString();
            car.CreatedAt = DateTime.UtcNow;
            car.LastUpdated = DateTime.UtcNow;

            var carJson = JsonSerializer.Serialize(car);
            return await _jsRuntime.InvokeAsync<bool>("firestore.addCar", carJson);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error adding car: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> AddCarsAsync(List<Car> cars)
    {
        try
        {
            var carsJson = JsonSerializer.Serialize(cars);
            return await _jsRuntime.InvokeAsync<bool>("firestore.addCars", carsJson);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error adding cars: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> UpdateCarAsync(Car car)
    {
        try
        {
            car.LastUpdated = DateTime.UtcNow;
            var carJson = JsonSerializer.Serialize(car);
            return await _jsRuntime.InvokeAsync<bool>("firestore.updateCar", carJson);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error updating car: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> DeleteCarAsync(string id)
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("firestore.deleteCar", id);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error deleting car: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> DeleteCarsByClientIdAsync(string clientId)
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("firestore.deleteCarsByClientId", clientId);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error deleting cars by client id: {ex.Message}");
            return false;
        }
    }
}
