namespace car_lister.Models;

public class Dealer
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string EntityId { get; set; } = "";
    public string Url { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
