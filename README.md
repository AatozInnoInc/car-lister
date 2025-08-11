# 🚗 Car Lister PWA

A modern Progressive Web App for scraping and listing cars from CarGurus.com. Built with Blazor WebAssembly frontend and Python FastAPI backend, deployed on Firebase.

## 🏗️ Architecture

```
car-lister/
├── frontend/                    # Blazor PWA (C#)
│   ├── Pages/                   # Blazor components
│   ├── Services/                # C# services
│   ├── wwwroot/                 # Static assets
│   └── car-lister.csproj       # .NET project file
├── backend/                     # Python API
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── scraper/               # Scraping module
│   └── README.md              # Backend documentation
├── firebase.json              # Firebase configuration
├── .firebaserc                # Firebase project settings
├── deploy.ps1                 # Deployment script
└── README.md                  # This file
```

## ✨ Features

### 🎨 Frontend (Blazor PWA)
- **Modern UI/UX**: iOS/meta-inspired design with glassmorphism
- **Progressive Web App**: Installable, offline-capable
- **Responsive Design**: Works on all devices
- **Real-time Updates**: Live car data scraping
- **Beautiful Animations**: Smooth transitions and effects

### 🐍 Backend (Python FastAPI)
- **Professional Scraping**: Robust CarGurus.com scraping
- **Multiple Strategies**: CSS selectors, regex, fallbacks
- **Error Handling**: Retry logic with exponential backoff
- **Async Performance**: Fast, concurrent requests
- **Type Safety**: Pydantic models for data validation

### 🔥 Firebase Integration
- **Hosting**: Blazor PWA deployment
- **Functions**: Python API deployment
- **Firestore**: Car data storage
- **Authentication**: Google Sign-in
- **Security Rules**: Data access control

## 🚀 Quick Start

### Prerequisites
- .NET 8.0 SDK
- Python 3.11+
- Firebase CLI
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd car-lister
```

### 2. Install Dependencies
```bash
# Frontend dependencies
dotnet restore

# Backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Configure Firebase
```bash
firebase login
firebase use car-lister-be093
```

### 4. Run Locally
```bash
# Start frontend (Blazor PWA)
dotnet run

# Start backend (Python API) - in another terminal
cd backend
python main.py
```

### 5. Deploy to Production

#### Backend Deployment (Render.com)
The backend API is automatically deployed to Render.com when changes are pushed to the main branch.

**Production API URL:** `https://car-lister-api.onrender.com`

#### Frontend Deployment (Firebase)
```bash
# Deploy frontend to Firebase
./deploy.ps1

# Or deploy specific parts
./deploy.ps1 -FrontendOnly
./deploy.ps1 -BackendOnly
```

## 🎯 Usage

### Adding a Car Listing
1. Navigate to the app
2. Click "Get Started" on "List Your Car"
3. Paste a CarGurus.com URL
4. Click "Scrape Car Details"
5. Review the scraped data
6. Click "Save Listing"

### Example URLs
- `https://www.cargurus.com/Cars/l-toyota-camry`
- `https://www.cargurus.com/Cars/l-honda-civic`
- `https://www.cargurus.com/Cars/l-ford-mustang`

## 🛠️ Development

### Frontend Development
```bash
# Run in development mode
dotnet run

# Build for production
dotnet build --configuration Release

# Run tests
dotnet test
```

### Backend Development
```bash
cd backend

# Run development server
python main.py

# Run tests
pytest tests/

# Format code
black .
```

### API Testing
```bash
# Test scraping endpoint (Production)
curl -X POST "https://car-lister-api.onrender.com/api/scrape" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789"}'

# Health check (Production)
curl "https://car-lister-api.onrender.com/api/health"

# Local development testing
curl -X POST "http://localhost:8000/api/scrape" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789"}'
```

## 📊 API Documentation

The Car Lister API provides comprehensive car data scraping capabilities with multiple endpoints for different use cases.

### Available Endpoints

- **POST `/api/scrape`** - Scrape individual car details from CarGurus.com
- **POST `/api/inventory/search`** - Search for cars by location and criteria
- **POST `/api/dealer/inventory`** - Scrape inventory from specific dealers
- **GET `/api/health`** - Health check for monitoring
- **GET `/api/cors-test`** - Test CORS functionality

### Quick API Examples

**Scrape Individual Car:**
```bash
curl -X POST "https://car-lister-api.onrender.com/api/scrape" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789"}'
```

**Search Inventory:**
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

**Scrape Dealer Inventory:**
```bash
curl -X POST "https://car-lister-api.onrender.com/api/dealer/inventory" \
     -H "Content-Type: application/json" \
     -d '{
       "entityId": "317131",
       "pageNumber": 1
     }'
```

### Complete API Documentation

For detailed API documentation including:
- Full OpenAPI 3.1.0 specification
- Request/response schemas
- Error handling
- Code examples in multiple languages
- Google Apps Script integration

See: [`backend/API_DOCUMENTATION.md`](backend/API_DOCUMENTATION.md)

### OpenAPI Specification

The complete OpenAPI specification is available at: [`backend/openapi.yaml`](backend/openapi.yaml)

### Google Apps Script Integration

For Google Apps Script integration examples, see: [`backend/google-apps-script-example.js`](backend/google-apps-script-example.js)

## 🏗️ Design Patterns

### Frontend (Blazor)
- **Component Pattern**: Reusable UI components
- **Service Pattern**: Dependency injection for services
- **Observer Pattern**: State management and updates
- **Factory Pattern**: Dynamic component creation

### Backend (Python)
- **Strategy Pattern**: Multiple scraping strategies
- **Factory Pattern**: Different extractors based on page type
- **Retry Pattern**: Exponential backoff for network requests
- **Repository Pattern**: Data access abstraction

## 🔒 Security

- **Input Validation**: URL sanitization and validation
- **CORS Protection**: Configured for Firebase domains
- **Rate Limiting**: To be implemented
- **Error Sanitization**: Safe error messages
- **Authentication**: Firebase Auth integration

## 📈 Performance

- **Async Operations**: Non-blocking I/O
- **Connection Pooling**: Efficient HTTP connections
- **Caching**: To be implemented
- **CDN**: Firebase hosting with global CDN
- **Compression**: Gzip compression enabled

## 🧪 Testing

### Frontend Tests
```bash
dotnet test
```

### Backend Tests
```bash
cd backend
pytest tests/
```

### Integration Tests
```bash
# Test full scraping workflow (Production)
curl -X POST "https://car-lister-api.onrender.com/api/scrape" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789"}'

# Test inventory search
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

## 📦 Deployment

### Manual Deployment
```bash
# Build frontend
dotnet build --configuration Release

# Deploy to Firebase
firebase deploy
```

### Automated Deployment
```bash
# Deploy everything
./deploy.ps1

# Deploy specific parts
./deploy.ps1 -FrontendOnly
./deploy.ps1 -BackendOnly
```

## 🔧 Configuration

### Environment Variables
Create `.env` files as needed:

**Backend (.env):**
```env
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30
```

### Firebase Configuration
Update `firebase.json` and `.firebaserc` for your project.

## 📊 Monitoring

- **Application Logs**: Firebase Functions logs
- **Performance Metrics**: Response times and success rates
- **Error Tracking**: Comprehensive error logging
- **Health Checks**: `/api/health` endpoint

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow coding standards:
   - C#: Microsoft C# conventions
   - Python: PEP 8 style guide
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create GitHub issues
- **Documentation**: Check `/backend/README.md` for API details
- **Firebase**: Check Firebase console for deployment status

## 🎉 Acknowledgments

- **Blazor Team**: For the amazing WebAssembly framework
- **FastAPI**: For the high-performance Python web framework
- **Firebase**: For the comprehensive hosting and backend services
- **CarGurus**: For providing the car listing data (respecting their terms of service)

---

**Built with ❤️ using modern web technologies** 