from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import uvicorn
import requests
import logging
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Car Lister API",
    description="Backend API for Car Lister PWA - CarGurus scraping service",
    version="1.0.0"
)

# Configure CORS for Firebase hosting and Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://car-lister-be093.web.app",
        "https://car-lister-be093.firebaseapp.com",
        "https://*.onrender.com",  # For Render deployment
        "http://localhost:5212",  # For development
        "http://localhost:3000"   # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarGurusScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
        self.max_retries = 3
        self.timeout = 30
    
    def scrape_car(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape car details from CarGurus.com"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting scrape for URL: {url}")
            
            # Validate URL
            if not self._is_valid_cargurus_url(url):
                logger.error(f"Invalid CarGurus URL: {url}")
                return None
            
            # Fetch HTML content
            html_content = self._fetch_html(url)
            if not html_content:
                return None
            
            # Parse HTML using html5lib
            soup = BeautifulSoup(html_content, 'html5lib')
            
            # Extract car data
            car_data = self._extract_car_data(soup, url)
            
            if car_data:
                processing_time = time.time() - start_time
                logger.info(f"Successfully scraped car in {processing_time:.2f}s: {car_data['make']} {car_data['model']} {car_data['year']}")
                return car_data
            else:
                logger.warning(f"Failed to extract car data from: {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def _is_valid_cargurus_url(self, url: str) -> bool:
        """Validate that the URL is a valid CarGurus.com URL"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ('http', 'https') and
                parsed.netloc in ('www.cargurus.com', 'cargurus.com') and
                '/Cars/' in parsed.path
            )
        except Exception:
            return False
    
    def _fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content with retry logic"""
        import time
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f"HTTP {response.status_code} for {url} (attempt {attempt + 1})")
                    
            except requests.Timeout:
                logger.warning(f"Timeout for {url} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error fetching {url} (attempt {attempt + 1}): {str(e)}")
            
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _extract_car_data(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """Extract car data using multiple strategies"""
        try:
            # Extract basic car information
            make = self._extract_make(soup)
            model = self._extract_model(soup)
            year = self._extract_year(soup)
            price = self._extract_price(soup)
            description = self._extract_description(soup)
            features = self._extract_features(soup)
            images = self._extract_images(soup, url)
            
            # Validate that we have at least basic information
            if not make or not model or year == 0:
                logger.warning(f"Insufficient car data extracted from {url}")
                return None
            
            return {
                "make": make,
                "model": model,
                "year": year,
                "price": price,
                "description": description,
                "features": features,
                "images": images,
                "original_url": url,
                "scraped_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting car data: {str(e)}")
            return None
    
    def _extract_make(self, soup: BeautifulSoup) -> str:
        """Extract car make using multiple selectors"""
        selectors = [
            'span[class*="make"]',
            'div[class*="vehicle-title"] span[class*="make"]',
            'h1[class*="title"] span[class*="make"]',
            'div[class*="car-info"] span[class*="make"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        # Fallback: try to extract from page title
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            # Common car makes to look for
            makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes', 'Audi', 'Lexus', 'Hyundai']
            for make in makes:
                if make.lower() in title_text.lower():
                    return make
        
        return "Unknown"
    
    def _extract_model(self, soup: BeautifulSoup) -> str:
        """Extract car model using multiple selectors"""
        selectors = [
            'span[class*="model"]',
            'div[class*="vehicle-title"] span[class*="model"]',
            'h1[class*="title"] span[class*="model"]',
            'div[class*="car-info"] span[class*="model"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return "Unknown"
    
    def _extract_year(self, soup: BeautifulSoup) -> int:
        """Extract car year using multiple strategies"""
        # Try various selectors
        year_selectors = [
            'span[class*="year"]',
            'div[class*="vehicle-title"] span[class*="year"]',
            'h1[class*="title"] span[class*="year"]'
        ]
        
        for selector in year_selectors:
            element = soup.select_one(selector)
            if element:
                year_text = element.get_text().strip()
                year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
                if year_match:
                    year = int(year_match.group())
                    if 1900 <= year <= 2030:
                        return year
        
        # Fallback: search in page content
        page_text = soup.get_text()
        year_match = re.search(r'\b(19|20)\d{2}\b', page_text)
        if year_match:
            year = int(year_match.group())
            if 1900 <= year <= 2030:
                return year
        
        return 2024  # Default year
    
    def _extract_price(self, soup: BeautifulSoup) -> float:
        """Extract car price using multiple strategies"""
        price_selectors = [
            'span[class*="price"]',
            'div[class*="price"]',
            'span[class*="listing-price"]',
            'div[class*="listing-price"]',
            'span[class*="car-price"]'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text().strip()
                # Remove currency symbols and commas
                price_text = re.sub(r'[^\d.]', '', price_text)
                try:
                    price = float(price_text)
                    if price > 0:
                        return price
                except ValueError:
                    continue
        
        return 0.0
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract car description"""
        desc_selectors = [
            'div[class*="description"]',
            'div[class*="overview"]',
            'div[class*="vehicle-description"]',
            'p[class*="description"]',
            'div[class*="car-description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                description = element.get_text().strip()
                if description and len(description) > 10:
                    return description
        
        return "No description available."
    
    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract car features"""
        features = []
        feature_selectors = [
            'div[class*="features"] li',
            'div[class*="specs"] li',
            'ul[class*="features"] li',
            'div[class*="vehicle-features"] li',
            'div[class*="car-features"] li'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for element in elements:
                feature = element.get_text().strip()
                if feature and feature not in features:
                    features.append(feature)
        
        if not features:
            features.append("Features not available")
        
        return features
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract car images"""
        images = []
        image_selectors = [
            'img[class*="vehicle-image"]',
            'img[class*="car-image"]',
            'div[class*="gallery"] img',
            'img[class*="listing-image"]',
            'div[class*="car-gallery"] img'
        ]
        
        for selector in image_selectors:
            elements = soup.select(selector)
            for element in elements:
                src = element.get('src')
                if src:
                    # Ensure URL is absolute
                    if not src.startswith('http'):
                        src = urljoin(base_url, src)
                    if src not in images:
                        images.append(src)
        
        # Add placeholder if no images found
        if not images:
            images.append("https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=800&h=600&fit=crop")
        
        return images

# Initialize scraper
scraper = CarGurusScraper()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Car Lister API is running", "version": "1.0.0"}

@app.post("/api/scrape")
async def scrape_cargurus(request: Dict[str, Any]):
    """
    Scrape car details from CarGurus.com
    
    Args:
        request: Dictionary containing the CarGurus URL
        
    Returns:
        Dictionary with scraped car data or error
    """
    try:
        url = request.get("url", "")
        logger.info(f"Starting scrape for URL: {url}")
        
        # Validate URL
        if not url.startswith("https://www.cargurus.com"):
            raise HTTPException(status_code=400, detail="Invalid CarGurus URL")
        
        # Scrape the car details
        car_data = scraper.scrape_car(url)
        
        if car_data:
            logger.info(f"Successfully scraped: {car_data['make']} {car_data['model']} {car_data['year']}")
            return {
                "success": True,
                "data": car_data,
                "error": None
            }
        else:
            logger.warning(f"Failed to scrape data from: {url}")
            return {
                "success": False,
                "data": None,
                "error": "Failed to extract car details from the provided URL"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {
            "success": False,
            "data": None,
            "error": f"Internal server error: {str(e)}"
        }

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
    uvicorn.run(app, host="0.0.0.0", port=8000) 