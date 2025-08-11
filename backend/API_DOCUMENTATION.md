# Car Lister API Documentation

## Overview

The Car Lister API is a powerful service that allows you to scrape car data from CarGurus.com. It provides endpoints for individual car scraping, inventory searches, and dealer-specific inventory retrieval.

**Base URL:** `https://car-lister-api.onrender.com`

## Quick Start

### 1. Test API Connection

```bash
curl -X GET "https://car-lister-api.onrender.com/api/health"
```

Expected response:
```json
{
  "status": "healthy",
  "service": "car-lister-api",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. Scrape a Single Car

```bash
curl -X POST "https://car-lister-api.onrender.com/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789"
  }'
```

### 3. Search Inventory

```bash
curl -X POST "https://car-lister-api.onrender.com/api/inventory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "zip": "90210",
    "distance": 50,
    "pageNumber": 1,
    "srpVariation": "DEALER_INVENTORY",
    "newUsed": "USED"
  }'
```

## API Endpoints

### Health Check Endpoints

#### GET `/`
Basic health check to verify the API is running.

**Response:**
```json
{
  "message": "Car Lister API is running",
  "version": "1.0.0"
}
```

#### GET `/api/health`
Detailed health check for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "car-lister-api",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/cors-test`
Test CORS functionality.

**Response:**
```json
{
  "message": "CORS is working!",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Car Scraping Endpoints

#### POST `/api/scrape`
Scrape detailed car information from a CarGurus.com URL.

**Request Body:**
```json
{
  "url": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "make": "Toyota",
    "model": "Camry",
    "year": 2022,
    "price": 25000.0,
    "description": "Clean, well-maintained Toyota Camry with low mileage.",
    "features": [
      "Bluetooth Connectivity",
      "Backup Camera",
      "Lane Departure Warning"
    ],
    "stats": [
      {
        "header": "Mileage",
        "value": "15,234 miles"
      },
      {
        "header": "Transmission",
        "value": "Automatic"
      }
    ],
    "images": [
      "https://images.cargurus.com/listing/123456789/1024x768.jpg"
    ],
    "originalUrl": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789",
    "fullTitle": "2022 Toyota Camry LE",
    "scrapedAt": "2024-01-01T12:00:00Z"
  },
  "error": null
}
```

### Inventory Search Endpoints

#### POST `/api/inventory/search`
Search for cars in CarGurus inventory based on location and parameters.

**Request Body:**
```json
{
  "zip": "90210",
  "distance": 50,
  "pageNumber": 1,
  "srpVariation": "DEALER_INVENTORY",
  "newUsed": "USED"
}
```

**Response:**
```json
{
  "success": true,
  "cars": [
    {
      "make": "Honda",
      "model": "Civic",
      "year": 2021,
      "price": 22000.0,
      "description": "2021 Honda Civic",
      "features": ["Bluetooth", "Backup Camera"],
      "stats": [
        {
          "header": "Mileage",
          "value": "18,500 miles"
        }
      ],
      "images": ["https://images.cargurus.com/listing/987654321/1024x768.jpg"],
      "originalUrl": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=987654321",
      "fullTitle": "2021 Honda Civic EX",
      "scrapedAt": "2024-01-01T12:00:00Z"
    }
  ],
  "totalResults": 45,
  "currentPage": 1,
  "totalPages": 3,
  "processingTime": 2.34,
  "errorMessage": null
}
```

### Dealer Inventory Endpoints

#### POST `/api/dealer/inventory`
Scrape inventory from a specific dealer.

**Request Body:**
```json
{
  "dealerEntityId": "317131",
  "dealerName": "ABC Motors",
  "dealerUrl": "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?entitySelectingHelper.selectedEntity=sp317131",
  "pageNumber": 1
}
```

**Response:**
```json
{
  "success": true,
  "cars": [
    {
      "make": "Ford",
      "model": "F-150",
      "year": 2023,
      "price": 45000.0,
      "description": "2023 Ford F-150 XLT",
      "features": ["4x4", "Towing Package", "Sync 4"],
      "stats": [
        {
          "header": "Mileage",
          "value": "8,500 miles"
        },
        {
          "header": "Transmission",
          "value": "10-Speed Automatic"
        }
      ],
      "images": ["https://images.cargurus.com/listing/111222333/1024x768.jpg"],
      "originalUrl": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=111222333&entitySelectingHelper.selectedEntity=sp317131",
      "fullTitle": "2023 Ford F-150 XLT",
      "scrapedAt": "2024-01-01T12:00:00Z"
    }
  ],
  "totalResults": 163,
  "currentPage": 1,
  "totalPages": 8,
  "hasNextPage": true,
  "processingTime": 3.45,
  "message": "Successfully scraped 23 cars from dealer page 1 (Total: 163)",
  "errorMessage": null
}
```

## Data Models

### ScrapedCar Object

```json
{
  "make": "string",           // Vehicle make (manufacturer)
  "model": "string",          // Vehicle model
  "year": "integer",          // Vehicle model year (1900-2030)
  "price": "number",          // Vehicle price in USD
  "description": "string",    // Vehicle description from listing
  "features": ["string"],     // Array of vehicle features
  "stats": [                  // Array of vehicle specifications
    {
      "header": "string",     // Stat name/label
      "value": "string"       // Stat value
    }
  ],
  "images": ["string"],       // Array of image URLs
  "originalUrl": "string",    // Original CarGurus listing URL
  "fullTitle": "string",      // Complete vehicle title
  "scrapedAt": "string"       // ISO 8601 timestamp
}
```

### Common Stats

The `stats` array typically includes:
- **Mileage**: Current vehicle mileage
- **Transmission**: Transmission type (Automatic, Manual, etc.)
- **Drivetrain**: FWD, RWD, AWD, 4WD
- **Fuel Type**: Gasoline, Diesel, Electric, Hybrid, etc.
- **Engine**: Engine specifications
- **Exterior Color**: Vehicle color
- **Interior Color**: Interior color
- **VIN**: Vehicle Identification Number
- **Stock Number**: Dealer stock number

## Error Handling

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "success": false,
  "data": null,
  "error": "Invalid CarGurus URL"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "data": null,
  "error": "Internal server error: Failed to extract car details"
}
```

## Rate Limiting & Best Practices

1. **Be Respectful**: The API includes built-in delays to respect CarGurus.com servers
2. **Batch Requests**: When possible, use inventory search instead of individual scraping
3. **Error Handling**: Always check the `success` field in responses
4. **Timeout**: Set reasonable timeouts (30+ seconds recommended)
5. **Retry Logic**: Implement exponential backoff for failed requests

## CORS Support

The API supports CORS for web applications:
- **Development**: All origins allowed
- **Production**: Specific origins configured

## Google Apps Script Integration

See `google-apps-script-example.js` for a complete Google Apps Script integration example.

### Basic Usage in Google Apps Script:

```javascript
function testApi() {
  const response = UrlFetchApp.fetch('https://car-lister-api.onrender.com/api/health');
  const data = JSON.parse(response.getContentText());
  Logger.log(data);
}

function scrapeCar(url) {
  const payload = { url: url };
  const response = UrlFetchApp.fetch('https://car-lister-api.onrender.com/api/scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    payload: JSON.stringify(payload)
  });
  return JSON.parse(response.getContentText());
}
```

## Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function scrapeCar(url) {
  try {
    const response = await axios.post('https://car-lister-api.onrender.com/api/scrape', {
      url: url
    });
    
    if (response.data.success) {
      console.log('Car scraped:', response.data.data.fullTitle);
      return response.data.data;
    } else {
      console.error('Scraping failed:', response.data.error);
      return null;
    }
  } catch (error) {
    console.error('API error:', error.message);
    return null;
  }
}

async function searchInventory(zip, distance = 50) {
  try {
    const response = await axios.post('https://car-lister-api.onrender.com/api/inventory/search', {
      zip: zip,
      distance: distance,
      pageNumber: 1,
      srpVariation: 'DEALER_INVENTORY',
      newUsed: 'USED'
    });
    
    if (response.data.success) {
      console.log(`Found ${response.data.cars.length} cars`);
      return response.data.cars;
    } else {
      console.error('Search failed:', response.data.errorMessage);
      return [];
    }
  } catch (error) {
    console.error('API error:', error.message);
    return [];
  }
}
```

### Python

```python
import requests
import json

def scrape_car(url):
    try:
        response = requests.post(
            'https://car-lister-api.onrender.com/api/scrape',
            json={'url': url},
            timeout=30
        )
        
        data = response.json()
        if data['success']:
            print(f"Car scraped: {data['data']['fullTitle']}")
            return data['data']
        else:
            print(f"Scraping failed: {data['error']}")
            return None
    except Exception as e:
        print(f"API error: {e}")
        return None

def search_inventory(zip_code, distance=50):
    try:
        response = requests.post(
            'https://car-lister-api.onrender.com/api/inventory/search',
            json={
                'zip': zip_code,
                'distance': distance,
                'pageNumber': 1,
                'srpVariation': 'DEALER_INVENTORY',
                'newUsed': 'USED'
            },
            timeout=30
        )
        
        data = response.json()
        if data['success']:
            print(f"Found {len(data['cars'])} cars")
            return data['cars']
        else:
            print(f"Search failed: {data['errorMessage']}")
            return []
    except Exception as e:
        print(f"API error: {e}")
        return []
```

## Support

For API support and questions:
- **Documentation**: This file and the OpenAPI spec
- **Examples**: See `google-apps-script-example.js`
- **Health Check**: Use `/api/health` to verify API status

## Version History

- **v1.0.0**: Initial release with car scraping, inventory search, and dealer inventory endpoints
