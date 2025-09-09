using Microsoft.JSInterop;
using car_lister.Models;
using System.Text.Json;

namespace car_lister.Services;

public class ClientService : BaseFirestoreService
{
    private readonly CarService _carService;

    public ClientService(IJSRuntime jsRuntime, CarService carService) : base(jsRuntime)
    {
        _carService = carService;
    }

    // Client operations
    public async Task<List<Client>> GetAllClientsAsync()
    {
        return await GetAllAsync<Client>("getAllClients");
    }

    public async Task<Client?> GetClientByIdAsync(string id)
    {
        return await GetByIdAsync<Client>(id, "getClientById");
    }

    public async Task<bool> AddClientAsync(Client client)
    {
        client.CreatedAt = DateTime.UtcNow;
        client.UpdatedAt = DateTime.UtcNow;

        try
        {
            var json = JsonSerializer.Serialize(client);
            var clientId = await _jsRuntime.InvokeAsync<string>("firestore.addClient", json);
            
            if (!string.IsNullOrEmpty(clientId))
            {
                client.Id = clientId; // Set the ID returned from Firestore
                return true;
            }
            
            return false;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error adding client: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> UpdateClientAsync(Client client)
    {
        client.UpdatedAt = DateTime.UtcNow;
        return await UpdateAsync(client, "updateClient");
    }

    public async Task<bool> DeleteClientAsync(string id)
    {
        return await DeleteAsync(id, "deleteClient");
    }

    // Client inventory operations - delegated to CarService
    public async Task<List<ScrapedCar>> GetClientInventoryAsync(string clientId)
    {
        return await _carService.GetClientInventoryAsync(clientId);
    }

    public async Task<bool> AddToClientInventoryAsync(string clientId, ScrapedCar car)
    {
        return await _carService.AddToClientInventoryAsync(clientId, car);
    }

    public async Task<bool> AddMultipleToClientInventoryAsync(string clientId, List<ScrapedCar> cars)
    {
        return await _carService.AddMultipleToClientInventoryAsync(clientId, cars);
    }

    public async Task<bool> UpdateClientInventoryCarAsync(string clientId, ScrapedCar car)
    {
        return await _carService.UpdateClientInventoryCarAsync(clientId, car);
    }

    public async Task<bool> DeleteFromClientInventoryAsync(string clientId, string carId)
    {
        return await _carService.DeleteFromClientInventoryAsync(clientId, carId);
    }

    public async Task<bool> ClearClientInventoryAsync(string clientId)
    {
        return await _carService.ClearClientInventoryAsync(clientId);
    }
}
