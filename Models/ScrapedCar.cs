using System.Text.Json.Serialization;

namespace car_lister.Models
{
    public class ScrapedCar
    {
        [JsonPropertyName("make")]
        public string Make { get; set; } = "";

        [JsonPropertyName("model")]
        public string Model { get; set; } = "";

        [JsonPropertyName("year")]
        public int Year { get; set; }

        [JsonPropertyName("price")]
        public double Price { get; set; }

        [JsonPropertyName("description")]
        public string Description { get; set; } = "";

        [JsonPropertyName("features")]
        public List<string> Features { get; set; } = new();

        [JsonPropertyName("stats")]
        public List<object> Stats { get; set; } = new();

        [JsonPropertyName("images")]
        public List<string> Images { get; set; } = new();

        [JsonPropertyName("originalUrl")]
        public string OriginalUrl { get; set; } = "";

        [JsonPropertyName("fullTitle")]
        public string FullTitle { get; set; } = "";

        [JsonPropertyName("scrapedAt")]
        public DateTime ScrapedAt { get; set; }

        // Additional properties that might be useful
        [JsonPropertyName("vin")]
        public string VIN { get; set; } = "";

        [JsonPropertyName("stockNumber")]
        public string StockNumber { get; set; } = "";

        [JsonPropertyName("mileage")]
        public int Mileage { get; set; }

        [JsonPropertyName("exteriorColor")]
        public string ExteriorColor { get; set; } = "";

        [JsonPropertyName("interiorColor")]
        public string InteriorColor { get; set; } = "";

        [JsonPropertyName("bodyStyle")]
        public string BodyStyle { get; set; } = "";

        [JsonPropertyName("condition")]
        public string Condition { get; set; } = "";

        [JsonPropertyName("transmission")]
        public string Transmission { get; set; } = "";

        [JsonPropertyName("drivetrain")]
        public string Drivetrain { get; set; } = "";

        [JsonPropertyName("engine")]
        public string Engine { get; set; } = "";

        [JsonPropertyName("fuelType")]
        public string FuelType { get; set; } = "";

        [JsonPropertyName("photoCount")]
        public int PhotoCount { get; set; }

        [JsonPropertyName("msrp")]
        public double MSRP { get; set; }

        [JsonPropertyName("marketDays")]
        public int MarketDays { get; set; }

        [JsonPropertyName("listingUrl")]
        public string ListingUrl { get; set; } = "";

        [JsonPropertyName("dataSource")]
        public string DataSource { get; set; } = "";

        [JsonPropertyName("enhancementStatus")]
        public string EnhancementStatus { get; set; } = "";

        [JsonPropertyName("enhancementDate")]
        public DateTime EnhancementDate { get; set; }

        [JsonPropertyName("highwayMPG")]
        public int HighwayMPG { get; set; }

        [JsonPropertyName("cityMPG")]
        public int CityMPG { get; set; }

        // For photo selection workflow
        [JsonPropertyName("photoUrls")]
        public List<string> PhotoUrls { get; set; } = new();

        [JsonPropertyName("selectedPhotoUrls")]
        public List<string> SelectedPhotoUrls { get; set; } = new();

        // Client relationship
        [JsonPropertyName("clientId")]
        public string ClientId { get; set; } = "";

        [JsonPropertyName("id")]
        public string Id { get; set; } = "";
    }
}
