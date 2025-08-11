# Dealer Management System

This document describes the dealer management functionality that has been added to the Car Lister application.

## Overview

The dealer management system allows administrators to manage dealers in the Firebase database instead of using hard-coded dealer lists. This provides flexibility to add, edit, and remove dealers without requiring code changes.

## Database Structure

### Dealer Collection (`dealers`)

Each dealer document contains the following fields:

- **Id** (string): Unique identifier for the dealer (auto-generated)
- **Name** (string): Friendly name of the dealer
- **EntityId** (string): CarGurus entity ID for the dealer
- **Url** (string): CarGurus URL for the dealer
- **CreatedAt** (timestamp): When the dealer was created
- **UpdatedAt** (timestamp): When the dealer was last updated

## Features

### 1. Dealer Management Page (`/dealer-management`)

- **View all dealers**: Displays a grid of all dealers in the database
- **Add new dealers**: Modal form to add new dealers
- **Edit existing dealers**: Update dealer information
- **Delete dealers**: Remove dealers from the database
- **Refresh data**: Reload dealer list from database

### 2. Automatic Initialization

When the inventory page loads for the first time and no dealers exist in the database, the system automatically initializes with the original hard-coded dealers:

- Asheboro Chrysler Dodge Jeep Ram (EntityId: 317131)
- Flow Honda of Winston Salem (EntityId: 59155)

### 3. Integration with Inventory Page

The inventory page now:
- Loads dealers from the database instead of hard-coded list
- Automatically initializes default dealers if none exist
- Maintains the same user experience with dropdown selection

## Technical Implementation

### Files Created/Modified

1. **Models/Dealer.cs** - Dealer data model
2. **Services/DealerService.cs** - Service for dealer database operations
3. **Pages/DealerManagement.razor** - Admin interface for managing dealers
4. **wwwroot/css/dealer-management.css** - Styles for dealer management page
5. **wwwroot/js/firestore.js** - Updated with dealer CRUD operations
6. **Pages/Inventory.razor** - Updated to use database instead of hard-coded dealers
7. **Shared/NavMenu.razor** - Added navigation link to dealer management
8. **firestore.rules** - Updated security rules for dealers collection
9. **Program.cs** - Registered DealerService

### Firebase Operations

The system uses the following Firebase Firestore operations:

- `getAllDealers()` - Retrieve all dealers
- `getDealerById(id)` - Get specific dealer by ID
- `addDealer(dealerJson)` - Add new dealer
- `updateDealer(dealerJson)` - Update existing dealer
- `deleteDealer(id)` - Delete dealer by ID

### Security Rules

The Firestore security rules allow:
- **Read access**: All authenticated users can view dealers
- **Write access**: All authenticated users can create, update, and delete dealers (admin functionality)

## Usage

### For Administrators

1. Navigate to `/dealer-management` from the main navigation
2. Use the "Add New Dealer" button to add dealers
3. Click "Edit" on any dealer card to modify information
4. Click "Delete" to remove dealers (with confirmation)
5. Use "Refresh" to reload the dealer list

### For Users

1. Navigate to `/inventory` as usual
2. The dealer dropdown will now show dealers from the database
3. Functionality remains the same - select a dealer and search inventory

## Adding New Dealers

To add a new dealer, you'll need:

1. **Dealer Name**: The friendly name displayed to users
2. **Entity ID**: The CarGurus entity ID (found in the dealer's CarGurus URL)
3. **URL**: The full CarGurus URL for the dealer

Example:
- Name: "ABC Motors"
- Entity ID: "123456"
- URL: "https://www.cargurus.com/Cars/m-ABC-Motors-sp123456"

## Error Handling

The system includes comprehensive error handling:

- Database connection errors
- Invalid data validation
- Network timeouts
- User confirmation for destructive actions
- Fallback to empty lists if database is unavailable

## Future Enhancements

Potential improvements for the dealer management system:

1. **User Roles**: Implement role-based access control for dealer management
2. **Bulk Operations**: Import/export dealers via CSV
3. **Dealer Categories**: Group dealers by region or type
4. **Dealer Status**: Active/inactive dealer status
5. **Audit Trail**: Track who made changes and when
6. **Dealer Analytics**: Track which dealers are most popular

## Troubleshooting

### Common Issues

1. **Dealers not loading**: Check Firebase connection and authentication
2. **Cannot add dealers**: Verify user is authenticated and has proper permissions
3. **Changes not saving**: Check browser console for JavaScript errors
4. **Page not accessible**: Ensure user is logged in (page requires authentication)

### Debug Information

Enable browser developer tools to see:
- Firebase connection status
- Database operation logs
- Error messages and stack traces
- Network requests to Firebase
