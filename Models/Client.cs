namespace car_lister.Models;

public class Client
{
    public Client()
    {
        Id = Guid.NewGuid().ToString();
    }

    public Client(string id)
    {
        Id = id;
    }


    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string DealerUrl { get; set; } = "";
    public string Location { get; set; } = "";
    public string DataSource { get; set; } = ""; // Cars.com, CarGurus, MarketCheck, CarsForSale
    public string VehicleFilter { get; set; } = "Used Only"; // Used Only, New Only, Both
    public bool OwnedInventoryOnly { get; set; } = false;
    public string? CarGurusEntityId { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? LastUpdate { get; set; } = null;
    public int VehicleCount { get; set; } = 0;
    public int EnhancedCount { get; set; } = 0;
    public bool IsActive { get; set; } = true;
}

public class Car
{
    public string Id { get; set; } = "";
    public string ClientId { get; set; } = "";
    public string StockNumber { get; set; } = "";
    public string VIN { get; set; } = "";
    public int Year { get; set; }
    public string Make { get; set; } = "";
    public string Model { get; set; } = "";
    public string Trim { get; set; } = "";  
    public decimal Price { get; set; }
    public int Mileage { get; set; }
    public string ExteriorColor { get; set; } = "";
    public string InteriorColor { get; set; } = "";
    public string BodyStyle { get; set; } = "";
    public string Condition { get; set; } = "";
    public string Transmission { get; set; } = "";
    public string Drivetrain { get; set; } = "";
    public string Engine { get; set; } = "";
    public string FuelType { get; set; } = "";
    public List<string> PhotoUrls { get; set; } = new();
    public List<string> SelectedPhotoUrls { get; set; } = new();
    public int PhotoCount { get; set; }
    public decimal? MSRP { get; set; }
    public int MarketDays { get; set; }
    public string ListingUrl { get; set; } = "";
    public string DataSource { get; set; } = "";
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    public string EnhancementStatus { get; set; } = "";
    public DateTime? EnhancementDate { get; set; }
    public int? HighwayMPG { get; set; }
    public int? CityMPG { get; set; }
    public string? MarketCheckId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
