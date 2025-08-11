using Microsoft.JSInterop;
using car_lister.Models;
using System.Text.Json;

namespace car_lister.Services;

public class DealerService
{
    private readonly IJSRuntime _jsRuntime;

    public DealerService(IJSRuntime jsRuntime)
    {
        _jsRuntime = jsRuntime;
    }

    public async Task<List<Dealer>> GetAllDealersAsync()
    {
        try
        {
            var dealersJson = await _jsRuntime.InvokeAsync<string>("firestore.getAllDealers");
            if (string.IsNullOrEmpty(dealersJson) || dealersJson == "[]")
            {
                return new List<Dealer>();
            }

            var dealers = JsonSerializer.Deserialize<List<Dealer>>(dealersJson, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            return dealers ?? new List<Dealer>();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting dealers: {ex.Message}");
            return new List<Dealer>();
        }
    }

    public async Task<Dealer?> GetDealerByIdAsync(string id)
    {
        try
        {
            var dealerJson = await _jsRuntime.InvokeAsync<string>("firestore.getDealerById", id);
            if (string.IsNullOrEmpty(dealerJson))
            {
                return null;
            }

            return JsonSerializer.Deserialize<Dealer>(dealerJson, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting dealer by id: {ex.Message}");
            return null;
        }
    }

    public async Task<bool> AddDealerAsync(Dealer dealer)
    {
        try
        {
            dealer.Id = Guid.NewGuid().ToString();
            dealer.CreatedAt = DateTime.UtcNow;
            dealer.UpdatedAt = DateTime.UtcNow;

            var dealerJson = JsonSerializer.Serialize(dealer);
            return await _jsRuntime.InvokeAsync<bool>("firestore.addDealer", dealerJson);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error adding dealer: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> UpdateDealerAsync(Dealer dealer)
    {
        try
        {
            dealer.UpdatedAt = DateTime.UtcNow;
            var dealerJson = JsonSerializer.Serialize(dealer);
            return await _jsRuntime.InvokeAsync<bool>("firestore.updateDealer", dealerJson);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error updating dealer: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> DeleteDealerAsync(string id)
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("firestore.deleteDealer", id);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error deleting dealer: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> InitializeDefaultDealersAsync()
    {
        try
        {
            var existingDealers = await GetAllDealersAsync();
            if (existingDealers.Any())
            {
                return true; // Already initialized
            }

            var defaultDealers = new List<Dealer>
            {
                new Dealer
                {
                    Name = "Asheboro Chrysler Dodge Jeep Ram",
                    EntityId = "317131",
                    Url = "https://www.cargurus.com/Cars/m-Asheboro-Chrysler-Dodge-Jeep-Ram-sp317131"
                },
                new Dealer
                {
                    Name = "Flow Honda of Winston Salem",
                    EntityId = "59155",
                    Url = "https://www.cargurus.com/Cars/m-Flow-Honda-of-Winston-Salem-sp59155"
                }
            };

            foreach (var dealer in defaultDealers)
            {
                await AddDealerAsync(dealer);
            }

            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error initializing default dealers: {ex.Message}");
            return false;
        }
    }
}
