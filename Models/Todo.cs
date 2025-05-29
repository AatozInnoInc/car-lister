using System;
using System.Text.Json.Serialization;

namespace todo_pwa.Models;

public class Todo
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    [JsonPropertyName("userId")]
    public string UserId { get; set; }
    
    [JsonPropertyName("title")]
    public string Title { get; set; }
    
    [JsonPropertyName("description")]
    public string Description { get; set; }
    
    [JsonPropertyName("isCompleted")]
    public bool IsCompleted { get; set; }
    
    private DateTime _createdAt = DateTime.Now;  // Store in local time
    
    [JsonPropertyName("createdAt")]
    public DateTime CreatedAt
    {
        get => _createdAt;
        set => _createdAt = DateTime.SpecifyKind(value, DateTimeKind.Local);
    }
    
    private DateTime? _completedAt;
    
    [JsonPropertyName("completedAt")]
    public DateTime? CompletedAt
    {
        get => _completedAt;
        set => _completedAt = value.HasValue ? 
            DateTime.SpecifyKind(value.Value, DateTimeKind.Local) : null;
    }
    
    private DateTime? _reminderDateTime;
    
    [JsonPropertyName("reminderDateTime")]
    public DateTime? ReminderDateTime
    {
        get => _reminderDateTime;
        set => _reminderDateTime = value.HasValue ? 
            DateTime.SpecifyKind(value.Value, DateTimeKind.Local) : null;
    }
    
    [JsonIgnore] // This is computed property, don't serialize
    public bool HasReminder => ReminderDateTime.HasValue;
    
    [JsonPropertyName("isReminderAcknowledged")]
    public bool IsReminderAcknowledged { get; set; }
    
    [JsonPropertyName("reminderNote")]
    public string ReminderNote { get; set; }
} 