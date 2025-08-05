from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from scraper.cargurus_scraper import CarGurusScraper
from scraper.models import ScrapedCar
import logging
import functions_framework

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Car Lister API",
    description="Backend API for Car Lister PWA - CarGurus scraping service",
    version="1.0.0"
)

# Configure CORS for Firebase hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://car-lister-be093.web.app",
        "https://car-lister-be093.firebaseapp.com",
        "http://localhost:5212",  # For development
        "http://localhost:3000"   # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ScrapeRequest(BaseModel):
    url: str

class ScrapeResponse(BaseModel):
    success: bool
    data: Optional[ScrapedCar] = None
    error: Optional[str] = None

# Initialize scraper
scraper = CarGurusScraper()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Car Lister API is running", "version": "1.0.0"}

@app.post("/api/scrape", response_model=ScrapeResponse)
async def scrape_cargurus(request: ScrapeRequest):
    """
    Scrape car details from CarGurus.com
    
    Args:
        request: ScrapeRequest containing the CarGurus URL
        
    Returns:
        ScrapeResponse with scraped car data or error
    """
    try:
        logger.info(f"Starting scrape for URL: {request.url}")
        
        # Validate URL
        if not request.url.startswith("https://www.cargurus.com"):
            raise HTTPException(status_code=400, detail="Invalid CarGurus URL")
        
        # Scrape the car details
        car_data = await scraper.scrape_car(request.url)
        
        if car_data:
            logger.info(f"Successfully scraped: {car_data.make} {car_data.model} {car_data.year}")
            return ScrapeResponse(success=True, data=car_data)
        else:
            logger.warning(f"Failed to scrape data from: {request.url}")
            return ScrapeResponse(
                success=False, 
                error="Failed to extract car details from the provided URL"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping {request.url}: {str(e)}")
        return ScrapeResponse(
            success=False,
            error=f"Internal server error: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "service": "car-lister-api",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Firebase Functions entry point
@functions_framework.http
def car_lister_api(request):
    """Firebase Functions HTTP trigger for Car Lister API"""
    import asyncio
    from fastapi.middleware.wsgi import WSGIMiddleware
    from fastapi.responses import JSONResponse
    
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)
    
    # Convert Flask request to FastAPI request
    async def handle_request():
        # Create a mock request object for FastAPI
        from fastapi import Request
        from starlette.datastructures import State
        
        # Extract request data
        body = request.get_data()
        headers = dict(request.headers)
        
        # Create FastAPI request context
        scope = {
            "type": "http",
            "method": request.method,
            "path": request.path,
            "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
            "query_string": request.query_string,
        }
        
        # Handle different endpoints
        if request.path == "/" and request.method == "GET":
            return await root()
        elif request.path == "/api/scrape" and request.method == "POST":
            # Parse JSON body
            import json
            data = json.loads(body.decode())
            scrape_request = ScrapeRequest(url=data.get("url", ""))
            return await scrape_cargurus(scrape_request)
        elif request.path == "/api/health" and request.method == "GET":
            return await health_check()
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Endpoint not found"}
            )
    
    # Run async function
    result = asyncio.run(handle_request())
    
    # Add CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    if hasattr(result, 'body'):
        return (result.body, result.status_code, {**headers, **result.headers})
    else:
        import json
        return (json.dumps(result), 200, headers)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 