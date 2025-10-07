using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace car_lister.Services;

public class LazyPosterService(HttpClient httpClient)
{
    private readonly HttpClient _httpClient = httpClient;
    private const string BASE_URL = "https://us-central1-lazyposter.cloudfunctions.net";
    // Hardcoded token from Google Scripts
    private const string API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFubmFjYXJvbGluZWU0MTRAZ21haWwuY29tIiwidWlkIjoiMTAxOCIsImlhdCI6MTc1NTk1NzAyMiwiZXhwIjoxNzg3NDkzMDIyfQ.-mBmNN0OFtayN7VlOXTczB4DKK3IoeTpirnFNdvA60Y";

    /// <summary>
    /// Add a new listing to LazyPoster
    /// </summary>
    public async Task<LazyPosterResponse> AddListingAsync(LazyPosterListing listing)
    {
        try
        {
            var url = $"{BASE_URL}/addListing?token={Uri.EscapeDataString(API_TOKEN)}";
            var request = new HttpRequestMessage(HttpMethod.Post, url);
            request.Content = JsonContent.Create(new { listing }, null, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            });

            var response = await _httpClient.SendAsync(request);
            var content = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                return new LazyPosterResponse
                {
                    Success = false,
                    ErrorMessage = $"API call failed ({response.StatusCode}): {content}"
                };
            }

            var result = JsonSerializer.Deserialize<LazyPosterApiResponse>(content, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            // Extract the ID from response
            var tlpId = result?.Id ?? result?.Listing?.Id;

            return new LazyPosterResponse
            {
                Success = true,
                TlpId = tlpId,
                RawResponse = content
            };
        }
        catch (Exception ex)
        {
            return new LazyPosterResponse
            {
                Success = false,
                ErrorMessage = $"Exception: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Update an existing listing in LazyPoster
    /// </summary>
    public async Task<LazyPosterResponse> EditListingAsync(string tlpId, LazyPosterListing listing)
    {
        try
        {
            var url = $"{BASE_URL}/editListing/{Uri.EscapeDataString(tlpId)}?token={Uri.EscapeDataString(API_TOKEN)}";
            var request = new HttpRequestMessage(HttpMethod.Post, url);
            request.Content = JsonContent.Create(new { listing }, null, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            });

            var response = await _httpClient.SendAsync(request);
            var content = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                return new LazyPosterResponse
                {
                    Success = false,
                    ErrorMessage = $"API call failed ({response.StatusCode}): {content}"
                };
            }

            return new LazyPosterResponse
            {
                Success = true,
                TlpId = tlpId,
                RawResponse = content
            };
        }
        catch (Exception ex)
        {
            return new LazyPosterResponse
            {
                Success = false,
                ErrorMessage = $"Exception: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Delete a listing from LazyPoster
    /// </summary>
    public async Task<LazyPosterResponse> DeleteListingAsync(string tlpId)
    {
        try
        {
            var url = $"{BASE_URL}/deleteListing/{Uri.EscapeDataString(tlpId)}?token={Uri.EscapeDataString(API_TOKEN)}";
            var request = new HttpRequestMessage(HttpMethod.Delete, url);

            var response = await _httpClient.SendAsync(request);
            var content = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                return new LazyPosterResponse
                {
                    Success = false,
                    ErrorMessage = $"API call failed ({response.StatusCode}): {content}"
                };
            }

            return new LazyPosterResponse
            {
                Success = true,
                RawResponse = content
            };
        }
        catch (Exception ex)
        {
            return new LazyPosterResponse
            {
                Success = false,
                ErrorMessage = $"Exception: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Get an existing listing from LazyPoster
    /// </summary>
    public async Task<LazyPosterResponse> GetListingAsync(string tlpId)
    {
        try
        {
            var url = $"{BASE_URL}/getListing/{Uri.EscapeDataString(tlpId)}?token={Uri.EscapeDataString(API_TOKEN)}";
            var request = new HttpRequestMessage(HttpMethod.Get, url);

            var response = await _httpClient.SendAsync(request);
            var content = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                return new LazyPosterResponse
                {
                    Success = false,
                    ErrorMessage = $"API call failed ({response.StatusCode}): {content}"
                };
            }

            var result = JsonSerializer.Deserialize<LazyPosterListing>(content, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            return new LazyPosterResponse
            {
                Success = true,
                Listing = result,
                RawResponse = content
            };
        }
        catch (Exception ex)
        {
            return new LazyPosterResponse
            {
                Success = false,
                ErrorMessage = $"Exception: {ex.Message}"
            };
        }
    }
}

// Models for LazyPoster API

public class LazyPosterListing
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "vehicle";

    [JsonPropertyName("campaign")]
    public string Campaign { get; set; } = "";

    [JsonPropertyName("platform")]
    public List<string> Platform { get; set; } = new() { "facebook" };

    [JsonPropertyName("postingAs")]
    public string PostingAs { get; set; } = "business";

    [JsonPropertyName("vehicleType")]
    public string VehicleType { get; set; } = "Car/Truck";

    [JsonPropertyName("offerupCategory")]
    public string OfferupCategory { get; set; } = "";

    [JsonPropertyName("offerupSubcategory")]
    public string OfferupSubcategory { get; set; } = "";

    [JsonPropertyName("title")]
    public string Title { get; set; } = "";

    [JsonPropertyName("price")]
    public double Price { get; set; }

    [JsonPropertyName("make")]
    public string Make { get; set; } = "";

    [JsonPropertyName("model")]
    public string Model { get; set; } = "";

    [JsonPropertyName("year")]
    public int Year { get; set; }

    [JsonPropertyName("mileage")]
    public int Mileage { get; set; }

    [JsonPropertyName("bodyStyle")]
    public string BodyStyle { get; set; } = "";

    [JsonPropertyName("colorExt")]
    public string ColorExt { get; set; } = "";

    [JsonPropertyName("colorInt")]
    public string ColorInt { get; set; } = "";

    [JsonPropertyName("condition")]
    public string Condition { get; set; } = "";

    [JsonPropertyName("fuel")]
    public string Fuel { get; set; } = "";

    [JsonPropertyName("transmission")]
    public string Transmission { get; set; } = "";

    [JsonPropertyName("titleStatus")]
    public string TitleStatus { get; set; } = "";

    [JsonPropertyName("location")]
    public string Location { get; set; } = "";

    [JsonPropertyName("description")]
    public string Description { get; set; } = "";

    [JsonPropertyName("images")]
    public List<string> Images { get; set; } = new();

    [JsonPropertyName("groups")]
    public List<string> Groups { get; set; } = new();

    [JsonPropertyName("includeMoreAdsLink")]
    public bool IncludeMoreAdsLink { get; set; } = true;
}

public class LazyPosterResponse
{
    public bool Success { get; set; }
    public string? TlpId { get; set; }
    public string? ErrorMessage { get; set; }
    public string? RawResponse { get; set; }
    public LazyPosterListing? Listing { get; set; }
}

// Internal response model for deserialization
internal class LazyPosterApiResponse
{
    [JsonPropertyName("id")]
    public string? Id { get; set; }

    [JsonPropertyName("listing")]
    public LazyPosterApiListing? Listing { get; set; }

    [JsonPropertyName("message")]
    public string? Message { get; set; }
}

internal class LazyPosterApiListing
{
    [JsonPropertyName("id")]
    public string? Id { get; set; }
}

