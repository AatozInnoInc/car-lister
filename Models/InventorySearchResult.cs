using System.Text.Json.Serialization;

namespace car_lister.Models
{
    public class InventorySearchResult
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("cars")]
        public List<ScrapedCar> Cars { get; set; } = new();

        [JsonPropertyName("totalResults")]
        public int TotalResults { get; set; }

        [JsonPropertyName("currentPage")]
        public int CurrentPage { get; set; }

        [JsonPropertyName("totalPages")]
        public int TotalPages { get; set; }

        [JsonPropertyName("hasNextPage")]
        public bool HasNextPage { get; set; }

        [JsonPropertyName("errorMessage")]
        public string? ErrorMessage { get; set; }

        [JsonPropertyName("processingTime")]
        public double ProcessingTime { get; set; }

        [JsonPropertyName("message")]
        public string? Message { get; set; }
    }
}
