from pydantic import BaseModel, Field
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
        original_url: Original CarGurus URL
        full_title: Complete car title (Year Make Model Trim)
        scraped_at: Timestamp when data was scraped
    """
    make: str = Field(..., description="Car manufacturer")
    model: str = Field(..., description="Car model")
    year: int = Field(..., description="Manufacturing year", ge=1900, le=2030)
    price: float = Field(..., description="Car price in USD", ge=0)
    description: str = Field(default="", description="Car description")
    features: List[str] = Field(default_factory=list, description="List of car features")
    stats: List[dict] = Field(default_factory=list, description="List of car statistics (header/value pairs)")
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    original_url: str = Field(..., description="Original CarGurus URL")
    full_title: str = Field(default="", description="Complete car title (Year Make Model Trim)")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="Scraping timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "make": "Toyota",
                "model": "Camry",
                "year": 2022,
                "price": 28500.0,
                "description": "This 2022 Toyota Camry offers excellent fuel economy...",
                "features": ["Bluetooth Connectivity", "Backup Camera", "Lane Departure Warning"],
                "stats": [{"header": "Mileage", "value": "15,000 miles"}, {"header": "Transmission", "value": "Automatic"}],
                "images": ["https://example.com/car1.jpg", "https://example.com/car2.jpg"],
                "original_url": "https://www.cargurus.com/Cars/l-toyota-camry",
                "full_title": "2022 Toyota Camry LE",
                "scraped_at": "2024-01-01T12:00:00Z"
            }
        }

class ScrapingResult(BaseModel):
    """
    Model representing the result of a scraping operation
    
    Attributes:
        success: Whether scraping was successful
        car_data: Scraped car data if successful
        error_message: Error message if failed
        processing_time: Time taken to process the request
    """
    success: bool = Field(..., description="Whether scraping was successful")
    car_data: Optional[ScrapedCar] = Field(None, description="Scraped car data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        schema_extra = {
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
                    "original_url": "https://www.cargurus.com/Cars/l-toyota-camry",
                    "full_title": "2022 Toyota Camry LE",
                    "scraped_at": "2024-01-01T12:00:00Z"
                },
                "error_message": None,
                "processing_time": 2.5
            }
        } 