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
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Car Lister API",
    description="Backend API for Car Lister PWA - CarGurus scraping service",
    version="1.0.0"
)

# Configure CORS for all possible frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for development
        "http://localhost:5212",  # Blazor development server
        "http://localhost:3000",  # Alternative development port
        "http://127.0.0.1:5212",  # Localhost alternative
        "https://car-lister-be093.web.app",  # Production
        "https://car-lister-be093.firebaseapp.com",  # Production
        "https://car-lister.web.app",  # Production
        "https://car-lister.firebaseapp.com"  # Production
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Pydantic models for inventory search
class InventorySearchRequest(BaseModel):
    zip: str
    distance: int = 100
    srpVariation: str = "NEW_CAR_SEARCH"
    pageNumber: int = 1
    newUsed: int = 1

class InventorySearchResult(BaseModel):
    success: bool
    cars: List[Dict[str, Any]] = []
    totalResults: int = 0
    currentPage: int = 1
    totalPages: int = 1
    errorMessage: Optional[str] = None
    processingTime: float = 0.0

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
                processingTime = time.time() - start_time
                logger.info(f"Successfully scraped car in {processingTime:.2f}s: {car_data['make']} {car_data['model']} {car_data['year']}")
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
        
        logger.info(f"Fetching HTML from URL: {url}")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} to fetch {url}")
                response = self.session.get(url, timeout=self.timeout)
                
                logger.info(f"HTTP response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    content_length = len(response.text)
                    logger.info(f"Successfully fetched HTML content: {content_length} characters")
                    return response.text
                else:
                    logger.warning(f"HTTP {response.status_code} for {url} (attempt {attempt + 1})")
                    logger.warning(f"Response content preview: {response.text[:500]}...")
                    
            except requests.Timeout:
                logger.warning(f"Timeout for {url} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error fetching {url} (attempt {attempt + 1}): {str(e)}")
            
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        logger.error(f"Failed to fetch HTML after {self.max_retries} attempts")
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
                "originalUrl": url,
                "scrapedAt": datetime.utcnow().isoformat()
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

    def search_inventory(self, request: InventorySearchRequest) -> InventorySearchResult:
        """Search for cars in CarGurus inventory"""
        start_time = time.time()
        
        try:
            logger.info(f"=== STARTING INVENTORY SEARCH ===")
            logger.info(f"Request parameters: ZIP={request.zip}, Distance={request.distance}, Page={request.pageNumber}, srpVariation={request.srpVariation}, newUsed={request.newUsed}")
            
            # Construct the search URL
            base_url = "https://www.cargurus.com/Cars/searchPage.action"
            params = {
                "newUsed": request.newUsed,
                "zip": request.zip,
                "distance": request.distance,
                "sourceContext": "carGurusHomePageModel",
                "srpVariation": request.srpVariation,
                "isDeliveryEnabled": "true",
                "nonShippableBaseline": "0",
                "pageNumber": request.pageNumber
            }
            
            # Build the URL
            url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            logger.info(f"CarGurus search URL: {url}")
            
            # Fetch the search page
            logger.info("Fetching content from CarGurus...")
            html_content = self._fetch_html(url)
            
            if not html_content:
                logger.error("Failed to fetch content from CarGurus")
                return InventorySearchResult(
                    success=False,
                    errorMessage="Failed to fetch search results",
                    processingTime=time.time() - start_time
                )
            
            logger.info(f"Successfully fetched content (length: {len(html_content)} characters)")
            
            # Check if this is a JSON response
            try:
                import json
                json_data = json.loads(html_content)
                logger.info("Detected JSON response from CarGurus")
                
                # Extract cars from JSON response
                cars = self._extract_cars_from_json(json_data)
                
                logger.info(f"Extracted {len(cars)} cars from JSON response")
                
                # Estimate total results and pages
                total_results = len(cars) * 20  # Rough estimate
                total_pages = max(1, (total_results + 19) // 20)  # 20 cars per page estimate
                
                processing_time = time.time() - start_time
                
                logger.info(f"=== INVENTORY SEARCH COMPLETE ===")
                logger.info(f"Found {len(cars)} cars in {processing_time:.2f}s")
                logger.info(f"Estimated total results: {total_results}, total pages: {total_pages}")
                
                return InventorySearchResult(
                    success=True,
                    cars=cars,
                    totalResults=total_results,
                    currentPage=request.pageNumber,
                    totalPages=total_pages,
                    processingTime=processing_time
                )
                
            except json.JSONDecodeError:
                logger.info("Response is not JSON, treating as HTML")
                # Parse the HTML (existing code)
                soup = BeautifulSoup(html_content, 'html5lib')
                
                # Log some basic info about the page
                title = soup.find('title')
                if title:
                    logger.info(f"Page title: {title.get_text().strip()}")
                
                # Extract cars from the search results
                logger.info("Extracting car listings from search page...")
                cars = self._extract_cars_from_search_page(soup, url)
                
                logger.info(f"Extracted {len(cars)} cars from search page")
                
                # Estimate total results and pages (CarGurus doesn't always provide this info)
                total_results = len(cars) * 20  # Rough estimate
                total_pages = max(1, (total_results + 19) // 20)  # 20 cars per page estimate
                
                processing_time = time.time() - start_time
                
                logger.info(f"=== INVENTORY SEARCH COMPLETE ===")
                logger.info(f"Found {len(cars)} cars in {processing_time:.2f}s")
                logger.info(f"Estimated total results: {total_results}, total pages: {total_pages}")
                
                return InventorySearchResult(
                    success=True,
                    cars=cars,
                    totalResults=total_results,
                    currentPage=request.pageNumber,
                    totalPages=total_pages,
                    processingTime=processing_time
                )
            
        except Exception as e:
            logger.error(f"Error in inventory search: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return InventorySearchResult(
                success=False,
                errorMessage=f"Internal server error: {str(e)}",
                processingTime=time.time() - start_time
            )

    def _extract_cars_from_search_page(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract car listings from search page"""
        cars = []
        
        logger.info("=== EXTRACTING CARS FROM SEARCH PAGE ===")
        
        # Try to find car listings using common selectors
        car_selectors = [
            'div[class*="listing-card"]',
            'div[class*="car-listing"]',
            'div[class*="vehicle-card"]',
            'div[data-cg-car-id]',
            'article[class*="listing"]',
            'div[class*="result-item"]',
            'div[class*="search-result"]',
            'div[class*="listing"]'
        ]
        
        car_elements = []
        selected_selector = None
        
        logger.info("Trying different CSS selectors to find car listings...")
        for selector in car_selectors:
            elements = soup.select(selector)
            logger.info(f"Selector '{selector}': found {len(elements)} elements")
            if elements:
                car_elements = elements
                selected_selector = selector
                logger.info(f"Using selector: {selector}")
                break
        
        if not car_elements:
            logger.info("No car elements found with standard selectors, trying fallback approach...")
            # Fallback: try to find any car-related content
            car_elements = soup.find_all(['div', 'article'], class_=re.compile(r'.*car.*|.*listing.*|.*vehicle.*', re.I))
            logger.info(f"Fallback approach found {len(car_elements)} potential elements")
        
        if not car_elements:
            logger.warning("No car elements found at all! Returning mock data.")
            # Log some info about the page structure for debugging
            logger.info("Page structure analysis:")
            logger.info(f"Total div elements: {len(soup.find_all('div'))}")
            logger.info(f"Total article elements: {len(soup.find_all('article'))}")
            
            # Look for any elements with car-related classes or IDs
            car_related_elements = soup.find_all(attrs={'class': re.compile(r'.*car.*|.*listing.*|.*vehicle.*', re.I)})
            logger.info(f"Elements with car-related classes: {len(car_related_elements)}")
            
            # Log first few elements for debugging
            for i, elem in enumerate(car_related_elements[:5]):
                logger.info(f"Car-related element {i+1}: {elem.name} - classes: {elem.get('class', [])}")
        
        logger.info(f"Processing {len(car_elements)} car elements (limiting to 20)...")
        
        for i, car_element in enumerate(car_elements[:20]):
            try:
                logger.info(f"Processing car element {i+1}/{min(len(car_elements), 20)}")
                car_data = self._extract_car_from_listing(car_element, base_url)
                if car_data:
                    cars.append(car_data)
                    logger.info(f"Successfully extracted car: {car_data.get('make', 'Unknown')} {car_data.get('model', 'Unknown')} {car_data.get('year', 'Unknown')}")
                else:
                    logger.warning(f"Failed to extract car data from element {i+1}")
            except Exception as e:
                logger.warning(f"Error extracting car from listing {i+1}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(cars)} cars from search page")
        
        # If no cars found, return some sample data
        if not cars:
            logger.warning("No cars found, returning mock data for debugging purposes")
            cars = [
                {
                    "make": "Toyota",
                    "model": "Camry",
                    "year": 2022,
                    "price": 28500.0,
                    "description": "Sample car listing (mock data)",
                    "features": ["Bluetooth", "Backup Camera"],
                    "images": ["https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=800&h=600&fit=crop"],
                    "originalUrl": "https://www.cargurus.com/Cars/l-toyota-camry",
                    "fullTitle": "2022 Toyota Camry LE (Mock Data)",
                    "scrapedAt": datetime.utcnow().isoformat()
                }
            ]
        
        logger.info(f"=== CAR EXTRACTION COMPLETE: {len(cars)} cars found ===")
        return cars

    def _extract_car_from_listing(self, car_element, base_url: str) -> Optional[Dict[str, Any]]:
        """Extract car data from a listing element"""
        try:
            logger.info(f"Extracting car data from element: {car_element.name} (classes: {car_element.get('class', [])})")
            
            # Extract basic car information
            make = self._extract_text(car_element, ['[class*="make"]', '[class*="brand"]'])
            model = self._extract_text(car_element, ['[class*="model"]'])
            year = self._extract_year_from_text(self._extract_text(car_element, ['[class*="year"]']))
            price = self._extract_price_from_text(self._extract_text(car_element, ['[class*="price"]']))
            
            logger.info(f"Extracted basic info - Make: '{make}', Model: '{model}', Year: {year}, Price: {price}")
            
            # Extract URL
            url_element = car_element.find('a', href=True)
            original_url = urljoin(base_url, url_element['href']) if url_element else base_url
            logger.info(f"Extracted URL: {original_url}")
            
            # Extract title
            title = self._extract_text(car_element, ['[class*="title"]', '[class*="name"]', 'h1', 'h2', 'h3'])
            if not title:
                title = f"{year} {make} {model}" if make and model else "Car Listing"
            logger.info(f"Extracted title: {title}")
            
            # Extract images
            images = []
            img_elements = car_element.find_all('img', src=True)
            logger.info(f"Found {len(img_elements)} image elements")
            
            for img in img_elements:
                src = img.get('src')
                if src and not src.startswith('data:'):
                    if not src.startswith('http'):
                        src = urljoin(base_url, src)
                    images.append(src)
            
            if not images:
                images = ["https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=800&h=600&fit=crop"]
            
            logger.info(f"Extracted {len(images)} images")
            
            car_data = {
                "make": make or "Unknown",
                "model": model or "Unknown",
                "year": year or 2022,
                "price": price or 0.0,
                "description": title,
                "features": [],
                "images": images,
                "originalUrl": original_url,
                "fullTitle": title,
                "scrapedAt": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully extracted car data: {car_data['make']} {car_data['model']} {car_data['year']}")
            return car_data
            
        except Exception as e:
            logger.warning(f"Error extracting car from listing: {e}")
            logger.warning(f"Exception type: {type(e).__name__}")
            return None

    def _extract_text(self, element, selectors: List[str]) -> str:
        """Extract text using multiple selectors"""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                text = found.get_text(strip=True)
                if text:
                    return text
        return ""

    def _extract_year_from_text(self, text: str) -> int:
        """Extract year from text"""
        if not text:
            return 2022
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            return int(year_match.group())
        return 2022

    def _extract_price_from_text(self, text: str) -> float:
        """Extract price from text"""
        if not text:
            return 0.0
        price_match = re.search(r'[\$]?[\d,]+(?:\.\d{2})?', text.replace(',', ''))
        if price_match:
            price_str = price_match.group().replace('$', '').replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                pass
        return 0.0

    def _extract_cars_from_json(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract car listings from JSON response"""
        cars = []
        
        logger.info("=== EXTRACTING CARS FROM JSON RESPONSE ===")
        
        # Check if we have tiles in the JSON response
        if 'tiles' not in json_data:
            logger.warning("No 'tiles' found in JSON response")
            return cars
        
        tiles = json_data['tiles']
        logger.info(f"Found {len(tiles)} tiles in JSON response")
        
        for i, tile in enumerate(tiles):
            try:
                logger.info(f"Processing tile {i+1}/{len(tiles)}")
                
                # Check if this is a car listing tile
                if not isinstance(tile, dict):
                    logger.warning(f"Tile {i+1} is not a dict: {type(tile)}")
                    continue
                
                tile_type = tile.get('type', '')
                tile_data = tile.get('data', {})
                
                logger.info(f"Tile type: {tile_type}, has data: {bool(tile_data)}")
                
                # Look for car listing tiles
                if tile_type in ['LISTING_NEW_PRIORITY', 'LISTING_USED_PRIORITY', 'LISTING_CERTIFIED_PRIORITY'] and tile_data:
                    car_data = self._extract_car_from_json_tile(tile_data)
                    if car_data:
                        cars.append(car_data)
                        logger.info(f"Successfully extracted car: {car_data.get('make', 'Unknown')} {car_data.get('model', 'Unknown')} {car_data.get('year', 'Unknown')}")
                    else:
                        logger.warning(f"Failed to extract car data from tile {i+1}")
                else:
                    logger.info(f"Skipping tile {i+1} - type: {tile_type}")
                    
            except Exception as e:
                logger.warning(f"Error processing tile {i+1}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(cars)} cars from JSON response")
        return cars
    
    def _extract_car_from_json_tile(self, tile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract car data from a JSON tile"""
        try:
            logger.info(f"Extracting car from tile data: {list(tile_data.keys())}")
            
            # Extract basic car information
            make = tile_data.get('makeName', 'Unknown')
            model = tile_data.get('modelName', 'Unknown')
            year = tile_data.get('carYear', 2024)
            price = tile_data.get('price', 0.0)
            
            # Extract title
            title = tile_data.get('listingTitle', '')
            if not title:
                title = f"{year} {make} {model}"
            
            # Extract description
            description = title
            
            # Extract features from options
            features = tile_data.get('options', [])
            
            # Extract images
            images = []
            original_picture_data = tile_data.get('originalPictureData', {})
            if original_picture_data and isinstance(original_picture_data, dict):
                image_url = original_picture_data.get('url', '')
                if image_url:
                    images.append(image_url)
            
            # If no images found, add placeholder
            if not images:
                images.append("https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=800&h=600&fit=crop")
            
            # Extract URL (construct from listing ID)
            listing_id = tile_data.get('id', '')
            original_url = f"https://www.cargurus.com/Cars/l-{listing_id}" if listing_id else "https://www.cargurus.com/Cars"
            
            # Extract additional info
            mileage = tile_data.get('mileage', 0)
            mileage_string = tile_data.get('mileageString', '0')
            exterior_color = tile_data.get('exteriorColorName', 'Unknown')
            dealer_name = tile_data.get('dealerName', 'Unknown')
            seller_city = tile_data.get('sellerCity', '')
            seller_region = tile_data.get('sellerRegion', '')
            
            car_data = {
                "make": make,
                "model": model,
                "year": year,
                "price": price,
                "description": description,
                "features": features,
                "images": images,
                "originalUrl": original_url,
                "fullTitle": title,
                "mileage": mileage,
                "mileageString": mileage_string,
                "exteriorColor": exterior_color,
                "dealerName": dealer_name,
                "sellerCity": seller_city,
                "sellerRegion": seller_region,
                "scrapedAt": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully extracted car data: {make} {model} {year} - ${price}")
            return car_data
            
        except Exception as e:
            logger.warning(f"Error extracting car from JSON tile: {e}")
            return None

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
        
        # Search the inventory
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