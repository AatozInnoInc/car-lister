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
        client.Id = Guid.NewGuid().ToString();
        client.CreatedAt = DateTime.UtcNow;
        client.UpdatedAt = DateTime.UtcNow;

        return await AddAsync(client, "addClient");
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

    // Car operations - delegated to CarService
    public async Task<List<Car>> GetCarsByClientIdAsync(string clientId)
    {
        return await _carService.GetLegacyCarsByClientIdAsync(clientId);
    }

    public async Task<bool> AddCarAsync(Car car)
    {
        return await _carService.AddLegacyCarsAsync(new List<Car> { car });
    }

    public async Task<bool> AddCarsAsync(List<Car> cars)
    {
        return await _carService.AddLegacyCarsAsync(cars);
    }

    public async Task<bool> UpdateCarAsync(Car car)
    {
        return await _carService.UpdateLegacyCarAsync(car);
    }

    public async Task<bool> DeleteCarAsync(string id)
    {
        return await _carService.DeleteCarAsync(id);
    }

    public async Task<bool> DeleteCarsByClientIdAsync(string clientId)
    {
        return await _carService.DeleteCarsByClientIdAsync(clientId);
    }
}
