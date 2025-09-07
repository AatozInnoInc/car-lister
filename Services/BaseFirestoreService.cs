using System.Text.Json;
using Microsoft.JSInterop;

namespace car_lister.Services
{
    public abstract class BaseFirestoreService
    {
        protected readonly IJSRuntime _jsRuntime;

        protected BaseFirestoreService(IJSRuntime jsRuntime)
        {
            _jsRuntime = jsRuntime;
        }

        protected async Task<List<T>> GetAllAsync<T>(string firestoreMethod)
        {
            try
            {
                var json = await _jsRuntime.InvokeAsync<string>($"firestore.{firestoreMethod}");
                if (string.IsNullOrEmpty(json) || json == "[]")
                {
                    return new List<T>();
                }

                var items = JsonSerializer.Deserialize<List<T>>(json, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                return items ?? new List<T>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting {typeof(T).Name} list: {ex.Message}");
                return new List<T>();
            }
        }

        protected async Task<T?> GetByIdAsync<T>(string id, string firestoreMethod)
        {
            try
            {
                var json = await _jsRuntime.InvokeAsync<string>($"firestore.{firestoreMethod}", id);
                if (string.IsNullOrEmpty(json))
                {
                    return default(T);
                }

                return JsonSerializer.Deserialize<T>(json, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting {typeof(T).Name} by id: {ex.Message}");
                return default(T);
            }
        }

        protected async Task<bool> AddAsync<T>(T item, string firestoreMethod)
        {
            try
            {
                var json = JsonSerializer.Serialize(item);
                return await _jsRuntime.InvokeAsync<bool>($"firestore.{firestoreMethod}", json);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error adding {typeof(T).Name}: {ex.Message}");
                return false;
            }
        }

        protected async Task<bool> UpdateAsync<T>(T item, string firestoreMethod)
        {
            try
            {
                var json = JsonSerializer.Serialize(item);
                return await _jsRuntime.InvokeAsync<bool>($"firestore.{firestoreMethod}", json);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error updating {typeof(T).Name}: {ex.Message}");
                return false;
            }
        }

        protected async Task<bool> DeleteAsync(string id, string firestoreMethod)
        {
            try
            {
                return await _jsRuntime.InvokeAsync<bool>($"firestore.{firestoreMethod}", id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error deleting {firestoreMethod}: {ex.Message}");
                return false;
            }
        }

        protected async Task<bool> DeleteByClientIdAsync(string clientId, string firestoreMethod)
        {
            try
            {
                return await _jsRuntime.InvokeAsync<bool>($"firestore.{firestoreMethod}", clientId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error deleting {firestoreMethod} by client id: {ex.Message}");
                return false;
            }
        }
    }
}
