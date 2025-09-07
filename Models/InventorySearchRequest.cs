using System.Text.Json.Serialization;

namespace car_lister.Models
{
    public class InventorySearchRequest
    {
        [JsonPropertyName("dealerEntityId")]
        public string DealerEntityId { get; set; } = "";

        [JsonPropertyName("dealerName")]
        public string DealerName { get; set; } = "";

        [JsonPropertyName("dealerUrl")]
        public string DealerUrl { get; set; } = "";

        [JsonPropertyName("pageNumber")]
        public int PageNumber { get; set; } = 1;

        [JsonPropertyName("inventoryType")]
        public string InventoryType { get; set; } = "ALL";

        // Additional parameters that might be needed
        [JsonPropertyName("zip")]
        public string? Zip { get; set; }

        [JsonPropertyName("distance")]
        public int Distance { get; set; } = 100;

        [JsonPropertyName("newUsed")]
        public string? NewUsed { get; set; }

        [JsonPropertyName("srpVariation")]
        public string? SrpVariation { get; set; }
    }
}
