using Microsoft.JSInterop;
using car_lister.Models;
using System.Text.Json;

namespace car_lister.Services;

public class DealerService : BaseFirestoreService
{
    public DealerService(IJSRuntime jsRuntime) : base(jsRuntime)
    {
    }

    public async Task<List<Dealer>> GetAllDealersAsync()
    {
        return await GetAllAsync<Dealer>("getAllDealers");
    }

    public async Task<Dealer?> GetDealerByIdAsync(string id)
    {
        return await GetByIdAsync<Dealer>(id, "getDealerById");
    }

    public async Task<bool> AddDealerAsync(Dealer dealer)
    {
        dealer.Id = Guid.NewGuid().ToString();
        dealer.CreatedAt = DateTime.UtcNow;
        dealer.UpdatedAt = DateTime.UtcNow;

        return await AddAsync(dealer, "addDealer");
    }

    public async Task<bool> UpdateDealerAsync(Dealer dealer)
    {
        dealer.UpdatedAt = DateTime.UtcNow;
        return await UpdateAsync(dealer, "updateDealer");
    }

    public async Task<bool> DeleteDealerAsync(string id)
    {
        return await DeleteAsync(id, "deleteDealer");
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
