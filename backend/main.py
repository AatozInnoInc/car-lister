from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from scraper.cargurus_scraper import CarGurusScraper
from scraper.models import ScrapedCar, InventorySearchRequest, InventorySearchResult, DealerInventoryRequest
import logging
import os


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Car Lister API",
    description="Backend API for Car Lister PWA - CarGurus scraping service",
    version="1.0.0"
)

# Configure CORS for all possible frontend origins
import os

# Get the environment to determine CORS settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    # Allow all origins for development
    allow_origins = ["*"]
    allow_credentials = False
else:
    # Specific origins for production
    allow_origins = [
        "https://car-lister-be093.web.app",
        "https://car-lister-be093.firebaseapp.com",
        "https://car-lister.web.app",
        "https://car-lister.firebaseapp.com",
        "https://car-lister-api.onrender.com",
        "http://localhost:5212",
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5212",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000"
    ]
    allow_credentials = False  # Changed to False to avoid preflight issues

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    max_age=3600  # Cache preflight requests for 1 hour
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

@app.get("/api/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {"message": "CORS is working!", "timestamp": "2024-01-01T00:00:00Z"}

@app.post("/api/scrape")
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
        car_data = scraper.scrape_car(request.url)
        
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

@app.post("/api/inventory/search")
async def search_inventory(request: InventorySearchRequest):
    """
    Search for cars in CarGurus inventory based on search parameters.
    
    Args:
        request: InventorySearchRequest containing search parameters
        
    Returns:
        InventorySearchResult with list of cars and pagination info
    """
    try:
        logger.info(f"Starting inventory search: ZIP={request.zip}, Distance={request.distance}, Page={request.pageNumber}")
        
        # Validate request parameters
        if not request.zip or len(request.zip) != 5:
            raise HTTPException(status_code=400, detail="Invalid ZIP code")
        
        if request.distance < 1 or request.distance > 500:
            raise HTTPException(status_code=400, detail="Distance must be between 1 and 500 miles")
        
        if request.pageNumber < 1:
            raise HTTPException(status_code=400, detail="Page number must be at least 1")
        
        # Use the original search method
        result = scraper.search_inventory(request)
        
        if result.success:
            logger.info(f"Successfully found {len(result.cars)} cars in inventory search")
            return result
        else:
            logger.warning(f"Inventory search failed: {result.errorMessage}")
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in inventory search: {str(e)}")
        return InventorySearchResult(
            success=False,
            errorMessage=f"Internal server error: {str(e)}",
            processingTime=0.0
        )

@app.post("/api/dealer/inventory")
async def scrape_dealer_inventory(request: DealerInventoryRequest):
    """
    Scrape inventory from a specific dealer using the improved AJAX method.
    
    Args:
        request: DealerInventoryRequest containing dealer entity ID, name, URL and page number
        
    Returns:
        InventorySearchResult with list of cars and pagination info
    """
    try:
        logger.info(f"Starting dealer inventory scrape: Dealer ID={request.dealerEntityId}, Name={request.dealerName}, Page={request.pageNumber}")
        
        # Validate request parameters
        if not request.dealerEntityId:
            raise HTTPException(status_code=400, detail="Dealer entity ID is required")
        
        if not request.dealerName:
            raise HTTPException(status_code=400, detail="Dealer name is required")
        
        if not request.dealerUrl:
            raise HTTPException(status_code=400, detail="Dealer URL is required")
        
        if not request.dealerUrl.startswith("https://www.cargurus.com"):
            raise HTTPException(status_code=400, detail="Invalid CarGurus dealer URL")
        
        if request.pageNumber < 1:
            raise HTTPException(status_code=400, detail="Page number must be at least 1")
        
        # Scrape the dealer inventory using the new AJAX method
        result = scraper.scrape_dealer_page(request.dealerEntityId, request.dealerUrl, request.pageNumber, request.inventoryType)
        
        if result.success:
            logger.info(f"Successfully found {len(result.cars)} cars from dealer {request.dealerName}")
            return result
        else:
            logger.warning(f"Dealer inventory scrape failed: {result.errorMessage}")
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in dealer inventory scrape: {str(e)}")
        return InventorySearchResult(
            success=False,
            errorMessage=f"Internal server error: {str(e)}",
            processingTime=0.0
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



if __name__ == "__main__":
    import asyncio
    uvicorn.run(app, host="0.0.0.0", port=8000) 