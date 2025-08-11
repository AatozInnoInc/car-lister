from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class ScrapedCar(BaseModel):
    """
    Model representing a scraped car from CarGurus.com
    
    Attributes:
        make: Car manufacturer (e.g., "Toyota", "Honda")
        model: Car model (e.g., "Camry", "Civic")
        year: Manufacturing year
        price: Car price in USD
        description: Car description/overview
        features: List of car features
        stats: List of car statistics (header/value pairs)
        images: List of image URLs
        originalUrl: Original CarGurus URL
        fullTitle: Complete car title (Year Make Model Trim)
        scrapedAt: Timestamp when data was scraped
    """
    make: str = Field(..., description="Car manufacturer")
    model: str = Field(..., description="Car model")
    year: int = Field(..., description="Manufacturing year", ge=1900, le=2030)
    price: float = Field(..., description="Car price in USD", ge=0)
    description: str = Field(default="", description="Car description")
    features: List[str] = Field(default_factory=list, description="List of car features")
    stats: List[dict] = Field(default_factory=list, description="List of car statistics (header/value pairs)")
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    originalUrl: str = Field(..., description="Original CarGurus URL")
    fullTitle: str = Field(default="", description="Complete car title (Year Make Model Trim)")
    scrapedAt: datetime = Field(default_factory=datetime.now, description="Scraping timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "make": "Toyota",
                "model": "Camry",
                "year": 2022,
                "price": 28500.0,
                "description": "This 2022 Toyota Camry offers excellent fuel economy...",
                "features": ["Bluetooth Connectivity", "Backup Camera", "Lane Departure Warning"],
                "stats": [{"header": "Mileage", "value": "15,000 miles"}, {"header": "Transmission", "value": "Automatic"}],
                "images": ["https://example.com/car1.jpg", "https://example.com/car2.jpg"],
                "originalUrl": "https://www.cargurus.com/Cars/l-toyota-camry",
                "fullTitle": "2022 Toyota Camry LE",
                "scrapedAt": "2024-01-01T12:00:00Z"
            }
        }
    )

class InventorySearchRequest(BaseModel):
    """
    Model representing an inventory search request
    
    Attributes:
        zip: ZIP code for search location
        distance: Search radius in miles
        srpVariation: Search variation type (e.g., "NEW_CAR_SEARCH", "USED_CAR_SEARCH")
        pageNumber: Page number for pagination
        newUsed: Type of cars to search (1=New, 2=Used, 3=Both)
    """
    zip: str = Field(..., description="ZIP code for search location")
    distance: int = Field(default=100, description="Search radius in miles", ge=1, le=500)
    srpVariation: str = Field(default="NEW_CAR_SEARCH", description="Search variation type")
    pageNumber: int = Field(default=1, description="Page number for pagination", ge=1)
    newUsed: int = Field(default=1, description="Type of cars to search (1=New, 2=Used, 3=Both)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "zip": "27401",
                "distance": 100,
                "srpVariation": "NEW_CAR_SEARCH",
                "pageNumber": 1,
                "newUsed": 1
            }
        }
    )

class DealerInventoryRequest(BaseModel):
    """
    Model representing a dealer inventory request
    
    Attributes:
        dealerEntityId: Dealer entity ID for dealer-specific searches
        dealerName: Human-readable dealer name
        dealerUrl: Full CarGurus dealer URL
        pageNumber: Page number for pagination
    """
    dealerEntityId: str = Field(..., description="Dealer entity ID for dealer-specific searches")
    dealerName: str = Field(..., description="Human-readable dealer name")
    dealerUrl: str = Field(..., description="Full CarGurus dealer URL")
    pageNumber: int = Field(default=1, description="Page number for pagination", ge=1)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dealerEntityId": "317131",
                "dealerName": "Asheboro Chrysler Dodge Jeep Ram",
                "dealerUrl": "https://www.cargurus.com/Cars/m-Asheboro-Chrysler-Dodge-Jeep-Ram-sp317131",
                "pageNumber": 1
            }
        }
    )

class InventorySearchResult(BaseModel):
    """
    Model representing the result of an inventory search
    
    Attributes:
        success: Whether search was successful
        cars: List of scraped cars from the search
        totalResults: Total number of results available
        currentPage: Current page number
        totalPages: Total number of pages
        hasNextPage: Whether there is a next page available
        hasPreviousPage: Whether there is a previous page available
        message: Success or error message
        errorMessage: Error message if failed
        processingTime: Time taken to process the request
    """
    success: bool = Field(..., description="Whether search was successful")
    cars: List[ScrapedCar] = Field(default_factory=list, description="List of scraped cars")
    totalResults: int = Field(default=0, description="Total number of results available")
    currentPage: int = Field(default=1, description="Current page number")
    totalPages: int = Field(default=1, description="Total number of pages")
    hasNextPage: bool = Field(default=False, description="Whether there is a next page available")
    hasPreviousPage: bool = Field(default=False, description="Whether there is a previous page available")
    message: Optional[str] = Field(None, description="Success or error message")
    errorMessage: Optional[str] = Field(None, description="Error message if failed")
    processingTime: float = Field(..., description="Processing time in seconds")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "cars": [
                    {
                        "make": "Toyota",
                        "model": "Camry",
                        "year": 2022,
                        "price": 28500.0,
                        "description": "This 2022 Toyota Camry...",
                        "features": ["Bluetooth Connectivity"],
                        "stats": [{"header": "Mileage", "value": "15,000 miles"}],
                        "images": ["https://example.com/car1.jpg"],
                        "originalUrl": "https://www.cargurus.com/Cars/l-toyota-camry",
                        "fullTitle": "2022 Toyota Camry LE",
                        "scrapedAt": "2024-01-01T12:00:00Z"
                    }
                ],
                "totalResults": 150,
                "currentPage": 1,
                "totalPages": 15,
                "hasNextPage": True,
                "hasPreviousPage": False,
                "message": "Successfully scraped 10 cars from page 1",
                "errorMessage": None,
                "processingTime": 2.5
            }
        }
    )

class ScrapingResult(BaseModel):
    """
    Model representing the result of a scraping operation
    
    Attributes:
        success: Whether scraping was successful
        car_data: Scraped car data if successful
        errorMessage: Error message if failed
        processingTime: Time taken to process the request
    """
    success: bool = Field(..., description="Whether scraping was successful")
    car_data: Optional[ScrapedCar] = Field(None, description="Scraped car data")
    errorMessage: Optional[str] = Field(None, description="Error message if failed")
    processingTime: float = Field(..., description="Processing time in seconds")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "car_data": {
                    "make": "Toyota",
                    "model": "Camry",
                    "year": 2022,
                    "price": 28500.0,
                    "description": "This 2022 Toyota Camry...",
                    "features": ["Bluetooth Connectivity"],
                    "stats": [{"header": "Mileage", "value": "15,000 miles"}],
                    "images": ["https://example.com/car1.jpg"],
                    "originalUrl": "https://www.cargurus.com/Cars/l-toyota-camry",
                    "fullTitle": "2022 Toyota Camry LE",
                    "scrapedAt": "2024-01-01T12:00:00Z"
                },
                "errorMessage": None,
                "processingTime": 2.5
            }
        }
    ) 