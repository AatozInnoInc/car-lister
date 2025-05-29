using Microsoft.JSInterop;
using System.Text.Json;
using todo_pwa.Models;

namespace todo_pwa.Services;

public class TodoService
{
    private readonly IJSRuntime _jsRuntime;

    public TodoService(IJSRuntime jsRuntime)
    {
        _jsRuntime = jsRuntime;
    }

    public async Task<List<Todo>> GetUserTodos(string userId)
    {
        try
        {
            var todos = await _jsRuntime.InvokeAsync<List<Todo>>("firestore.getUserTodos", userId);
            return todos ?? new List<Todo>();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting todos: {ex.Message}");
            return new List<Todo>();
        }
    }

    public async Task<bool> AddTodo(Todo todo)
    {
        try
        {
            var todoId = await _jsRuntime.InvokeAsync<string>("firestore.addTodo", todo);
            todo.Id = todoId; // Update the todo with the Firestore-generated ID
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error adding todo: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> UpdateTodo(Todo todo)
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("firestore.updateTodo", todo);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error updating todo: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> DeleteTodo(string todoId)
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("firestore.deleteTodo", todoId);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error deleting todo: {ex.Message}");
            return false;
        }
    }
} 