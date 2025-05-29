using Microsoft.JSInterop;
using System.Timers;
using todo_pwa.Models;

using Timer = System.Timers.Timer;

namespace todo_pwa.Services
{
    public class ReminderService : IDisposable
    {
        private readonly IJSRuntime _jsRuntime;
        private readonly TodoService _todoService;
        private Timer _checkTimer;
        private bool _isCheckingReminders;
        private string _currentUserId;

        public ReminderService(IJSRuntime jsRuntime, TodoService todoService)
        {
            _jsRuntime = jsRuntime;
            _todoService = todoService;
            
            // Check for reminders every minute
            _checkTimer = new Timer(60000); // 60 seconds
            _checkTimer.Elapsed += async (sender, e) => await CheckReminders();
        }

        public async Task Initialize(string userId)
        {
            _currentUserId = userId;
            await RequestNotificationPermission();
            await CheckReminders(); // Check immediately on initialization
            _checkTimer.Start();
        }

        public async Task RequestNotificationPermission()
        {
            try
            {
                await _jsRuntime.InvokeVoidAsync("notifications.requestPermission");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error requesting notification permission: {ex.Message}");
            }
        }

        private async Task CheckReminders()
        {
            if (_isCheckingReminders || string.IsNullOrEmpty(_currentUserId))
                return;

            _isCheckingReminders = true;

            try
            {
                Console.WriteLine($"Checking reminders at {DateTime.Now}");
                
                var upcomingReminders = await _jsRuntime.InvokeAsync<List<Todo>>(
                    "firestore.getUpcomingReminders",
                    _currentUserId
                );

                Console.WriteLine($"Found {upcomingReminders?.Count ?? 0} upcoming reminders");

                if (upcomingReminders != null)
                {
                    foreach (var todo in upcomingReminders)
                    {
                        if (todo.ReminderDateTime.HasValue)
                        {
                            var reminderTime = todo.ReminderDateTime.Value;
                            var now = DateTime.Now; // Use local time
                            var timeDiff = reminderTime - now;

                            Console.WriteLine($"Reminder '{todo.Title}' scheduled for {reminderTime:yyyy-MM-dd HH:mm:ss}");
                            Console.WriteLine($"Current time: {now:yyyy-MM-dd HH:mm:ss}");
                            Console.WriteLine($"Time difference: {timeDiff.TotalMinutes:F2} minutes");

                            // If the reminder is due within the next minute
                            if (timeDiff.TotalMinutes <= 1 && timeDiff.TotalMinutes > -1)
                            {
                                Console.WriteLine($"Showing notification for '{todo.Title}'");
                                await ShowNotification(todo);
                                
                                // Mark the reminder as acknowledged
                                todo.IsReminderAcknowledged = true;
                                await _todoService.UpdateTodo(todo);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error checking reminders: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
            }
            finally
            {
                _isCheckingReminders = false;
            }
        }

        private async Task ShowNotification(Todo todo)
        {
            try
            {
                var options = new
                {
                    body = string.IsNullOrEmpty(todo.ReminderNote) 
                        ? todo.Description 
                        : todo.ReminderNote,
                    requireInteraction = true,
                    tag = todo.Id // Prevent duplicate notifications
                };

                await _jsRuntime.InvokeVoidAsync(
                    "notifications.showNotification",
                    $"Reminder: {todo.Title}",
                    options
                );
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error showing notification: {ex.Message}");
            }
        }

        public void Dispose()
        {
            _checkTimer?.Dispose();
        }
    }
} 