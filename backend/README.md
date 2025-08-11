# Car Lister Python Backend

This is the Python FastAPI backend for the Car Lister PWA. It provides web scraping capabilities for CarGurus.com with professional architecture patterns.

## 🏗️ Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── scraper/               # Scraping module
│   ├── __init__.py
│   ├── cargurus_scraper.py  # Main scraper class
│   └── models.py          # Pydantic data models
└── utils/                 # Utility functions
    ├── __init__.py
    └── firebase_config.py # Firebase configuration
```

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Test dependencies (recommended):**
   ```bash
   python test_dependencies.py
   ```

3. **Run the development server:**
   ```bash
   python main.py
   ```

4. **Test the API:**
   ```bash
   curl -X POST "http://localhost:8000/api/scrape" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789"}'
   ```

### Render Deployment

The API is automatically deployed to Render.com when changes are pushed to the main branch.

**Production URL:** `https://car-lister-api.onrender.com`

1. **Deploy to Render:**
   ```bash
   # Push to your Git repository
   git add .
   git commit -m "Update dependencies for Render deployment"
   git push
   ```

2. **Monitor deployment:**
   - Check the Render dashboard for build logs
   - Verify the service starts successfully
   - Test the health endpoint: `https://car-lister-api.onrender.com/api/health`

3. **Test production API:**
   ```bash
   # Health check
   curl "https://car-lister-api.onrender.com/api/health"
   
   # Test scraping
   curl -X POST "https://car-lister-api.onrender.com/api/scrape" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789"}'
   ```

### Firebase Deployment

1. **Deploy to Firebase Functions:**
   ```bash
   firebase deploy --only functions
   ```

2. **Update frontend API URL:**
   Update the API URL in `Pages/AddListing.razor` to point to your Firebase Function.

## 📋 API Endpoints

The Car Lister API provides comprehensive car data scraping capabilities with the following endpoints:

### Core Endpoints

#### POST `/api/scrape`
Scrapes individual car details from CarGurus.com

**Request:**
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
    "price": 28500.0,
    "description": "This 2022 Toyota Camry...",
    "features": ["Bluetooth Connectivity", "Backup Camera"],
    "images": ["https://example.com/car1.jpg"],
    "originalUrl": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789",
    "scrapedAt": "2024-01-01T12:00:00Z"
  },
  "error": null
}
```

#### POST `/api/inventory/search`
Search for cars by location and criteria

**Request:**
```json
{
  "zip": "90210",
  "distance": 50,
  "pageNumber": 1,
  "srpVariation": "DEALER_INVENTORY",
  "newUsed": "USED"
}
```

#### POST `/api/dealer/inventory`
Scrape inventory from specific dealers

**Request:**
```json
{
  "entityId": "317131",
  "pageNumber": 1
}
```

### Utility Endpoints

#### GET `/api/health`
Health check endpoint for monitoring

#### GET `/api/cors-test`
Test CORS functionality

#### GET `/`
Basic health check

## 📚 Complete Documentation

For comprehensive API documentation including:
- Full OpenAPI 3.1.0 specification
- Request/response schemas with examples
- Error handling patterns
- Code examples in multiple languages
- Google Apps Script integration

See: [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md)

### OpenAPI Specification

The complete OpenAPI specification is available at: [`openapi.yaml`](openapi.yaml)

### Google Apps Script Integration

For Google Apps Script integration examples, see: [`google-apps-script-example.js`](google-apps-script-example.js)

## 🛠️ Design Patterns

### Strategy Pattern
The scraper uses multiple strategies to extract data:
- CSS selector strategies
- Regex fallback strategies
- Title-based extraction strategies

### Factory Pattern
Different extractors are created based on page type and content structure.

### Retry Pattern
Robust retry logic with exponential backoff for network requests.

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30
```

### CORS Configuration
The API is configured to allow requests from:
- Firebase hosting domains
- Local development servers

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/
```

## 📊 Monitoring

The API includes comprehensive logging:
- Request/response logging
- Error tracking
- Performance metrics
- Scraping success rates

## 🔒 Security

- Input validation for URLs
- Rate limiting (to be implemented)
- CORS protection
- Error message sanitization

## 🚀 Performance

- Async HTTP requests
- Connection pooling
- Efficient HTML parsing
- Caching (to be implemented)

## 📝 Contributing

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update documentation
4. Use type hints throughout

## 📚 Additional Documentation

This backend includes comprehensive documentation:

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API documentation with examples
- **[openapi.yaml](openapi.yaml)** - OpenAPI 3.1.0 specification
- **[google-apps-script-example.js](google-apps-script-example.js)** - Google Apps Script integration examples 