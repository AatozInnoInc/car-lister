import requests
import logging
import json
import re
import uuid
from typing import Optional, List
from urllib.parse import urlparse
from .models import ScrapedCar, InventorySearchRequest, InventorySearchResult
import time
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class CarGurusScraper:
    """
    Professional CarGurus.com scraper using the JSON API endpoint.
    
    This scraper uses CarGurus' internal JSON API to extract complete car data
    including all images, specifications, and detailed information.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.cargurus.com/',
        }
        self.session.headers.update(self.headers)
        self.max_retries = 3
        self.timeout = 30
    
    def scrape_car(self, url: str) -> Optional[ScrapedCar]:
        """
        Main scraping method using CarGurus JSON API.
        
        Args:
            url: CarGurus.com URL to scrape
            
        Returns:
            ScrapedCar object if successful, None otherwise
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting scrape for URL: {url}")
            
            # Validate URL
            if not self._is_valid_cargurus_url(url):
                logger.error(f"Invalid CarGurus URL: {url}")
                return None
            
            # Extract listing ID from URL
            listing_id = self._extract_listing_id(url)
            if not listing_id:
                logger.error(f"Could not extract listing ID from URL: {url}")
                logger.info(f"URL analysis - Domain: {urlparse(url).netloc}, Path: {urlparse(url).path}")
                return None
            
            logger.info(f"Extracted listing ID: {listing_id}")
            
            # Fetch JSON data from CarGurus API
            json_data = self._fetch_json_data(listing_id)
            if not json_data:
                logger.error(f"Failed to fetch JSON data for listing ID: {listing_id}")
                return None
            
            # Extract car data from JSON
            car_data = self._extract_car_data_from_json(json_data, url)
            
            if car_data:
                processingTime = time.time() - start_time
                logger.info(f"Successfully scraped car in {processingTime:.2f}s: {car_data.make} {car_data.model} {car_data.year}")
                return car_data
            else:
                logger.warning(f"Failed to extract car data from JSON for listing ID: {listing_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def search_inventory(self, request: InventorySearchRequest) -> InventorySearchResult:
        """
        Search for cars in CarGurus inventory based on search parameters.
        
        Args:
            request: InventorySearchRequest containing search parameters
            
        Returns:
            InventorySearchResult with list of cars and pagination info
        """
        start_time = time.time()
        
        try:
            logger.info(f"=== STARTING INVENTORY SEARCH ===")
            logger.info(f"Request parameters: ZIP={request.zip}, Distance={request.distance}, Page={request.pageNumber}, srpVariation={request.srpVariation}, newUsed={request.newUsed}")
            
            # Construct the search URL
            search_url = "https://www.cargurus.com/Cars/searchPage.action"
            
            # Generate a unique search ID for this search session
            search_id = str(uuid.uuid4())
            
            # Use the exact parameters that achieve consistency from the curl command
            params = {
                'newUsed': request.newUsed,
                'searchId': search_id,
                'zip': request.zip,
                'distance': request.distance,
                'sourceContext': 'carGurusHomePageModel',
                'sortDir': 'ASC',
                'sortType': 'BEST_MATCH',
                'srpVariation': request.srpVariation,
                'isDeliveryEnabled': 'true',
                'nonShippableBaseline': '0',
                'pageNumber': request.pageNumber,
                'filtersModified': 'true'
            }
            
            # Add pageReceipt for pages beyond the first (this helps with consistency)
            if request.pageNumber > 1:
                # For now, we'll skip pageReceipt as it's complex to generate
                # but we can add it later if needed for multi-page consistency
                pass
            
            logger.info(f"CarGurus search URL: {search_url} with params: {params}")
            
            # Update session headers to match the successful curl command
            self.session.headers.update({
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'dnt': '1',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'sec-ch-device-memory': '8',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-full-version-list': '"Not)A;Brand";v="8.0.0.0", "Chromium";v="138.0.7204.188", "Google Chrome";v="138.0.7204.188"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-cg-client-id': 'site-cars',
                'x-requested-with': 'XMLHttpRequest'
            })
            
            logger.info("Attempting search with enhanced parameters and headers for consistency")
            
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(search_url, params=params, timeout=self.timeout)
                    
                    logger.info(f"Response status: {response.status_code}")
                    logger.info(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
                    logger.info(f"Content length: {len(response.text)} characters")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        
                        # Check if this is a JSON response
                        if 'application/json' in content_type:
                            logger.info("Detected JSON response from CarGurus")
                            
                            try:
                                json_data = response.json()
                                logger.info(f"JSON response keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
                                
                                # Extract cars from JSON response
                                cars = self._extract_cars_from_json_response(json_data)
                                
                                if cars:
                                    processing_time = time.time() - start_time
                                    logger.info(f"Successfully found {len(cars)} cars in {processing_time:.2f}s")
                                    
                                    # Estimate total results and pages (CarGurus typically shows 20 cars per page)
                                    total_results = len(cars) * 20  # Rough estimate
                                    total_pages = max(1, (total_results + 19) // 20)
                                    
                                    return InventorySearchResult(
                                        success=True,
                                        cars=cars,
                                        totalResults=total_results,
                                        currentPage=request.pageNumber,
                                        totalPages=total_pages,
                                        processingTime=processing_time
                                    )
                                else:
                                    logger.warning("No cars found in JSON response")
                                    return InventorySearchResult(
                                        success=False,
                                        errorMessage="No cars found for the specified search criteria",
                                        processingTime=time.time() - start_time
                                    )
                                    
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse JSON response: {e}")
                                return InventorySearchResult(
                                    success=False,
                                    errorMessage=f"Failed to parse JSON response: {e}",
                                    processingTime=time.time() - start_time
                                )
                        
                        else:
                            logger.info("Response is not JSON, treating as HTML")
                            # Parse the HTML response to extract car listings
                            cars = self._extract_cars_from_search_page(response.text, request)
                            
                            if cars:
                                processing_time = time.time() - start_time
                                logger.info(f"Successfully found {len(cars)} cars in {processing_time:.2f}s")
                                
                                # Estimate total results and pages (CarGurus typically shows 20 cars per page)
                                total_results = len(cars) * 20  # Rough estimate
                                total_pages = max(1, (total_results + 19) // 20)
                                
                                return InventorySearchResult(
                                    success=True,
                                    cars=cars,
                                    totalResults=total_results,
                                    currentPage=request.pageNumber,
                                    totalPages=total_pages,
                                    processingTime=processing_time
                                )
                            else:
                                logger.warning("No cars found in HTML response")
                                return InventorySearchResult(
                                    success=False,
                                    errorMessage="No cars found for the specified search criteria",
                                    processingTime=time.time() - start_time
                                )
                    else:
                        logger.warning(f"HTTP {response.status_code} for search (attempt {attempt + 1})")
                        logger.warning(f"Response content preview: {response.text[:500]}...")
                        
                except requests.Timeout:
                    logger.warning(f"Timeout for search (attempt {attempt + 1})")
                except Exception as e:
                    logger.error(f"Error during search (attempt {attempt + 1}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            return InventorySearchResult(
                success=False,
                errorMessage="Failed to search inventory after multiple attempts",
                processingTime=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error in search_inventory: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return InventorySearchResult(
                success=False,
                errorMessage=f"Internal error: {str(e)}",
                processingTime=time.time() - start_time
            )

    def scrape_dealer_page(self, dealer_entity_id: str, dealer_url: str, page_number: int = 1, inventory_type: str = "ALL") -> InventorySearchResult:
        """
        Scrape dealer inventory using the AJAX pagination approach.
        This uses the searchPage.action endpoint that CarGurus uses for pagination.
        
        Args:
            dealer_entity_id: The dealer's entity ID (e.g., "317131")
            dealer_url: The full CarGurus dealer URL
            page_number: Page number to scrape (default: 1)
            inventory_type: Type of inventory to search (ALL, NEW, USED)
            
        Returns:
            InventorySearchResult with list of cars and pagination info
        """
        start_time = time.time()
        
        try:
            logger.info(f"=== STARTING DEALER PAGE SCRAPE (AJAX METHOD) ===")
            logger.info(f"Dealer Entity ID: {dealer_entity_id}, Dealer URL: {dealer_url}, Page: {page_number}, Inventory Type: {inventory_type}")
            
            # Use the provided dealer URL instead of hard-coding
            logger.info(f"Getting initial dealer page: {dealer_url}")
            
            # Get the initial page to extract search parameters
            response = self.session.get(dealer_url, timeout=self.timeout)
            
            if response.status_code != 200:
                logger.error(f"Failed to get initial dealer page: HTTP {response.status_code}")
                return InventorySearchResult(
                    success=False,
                    cars=[],
                    totalResults=0,
                    currentPage=page_number,
                    totalPages=0,
                    hasNextPage=False,
                    processingTime=time.time() - start_time,
                    message=f"Failed to get initial dealer page: HTTP {response.status_code}"
                )
            
            # Extract search parameters from the initial page
            search_params = self._extract_search_params_from_dealer_page(response.text, dealer_entity_id, inventory_type)
            
            if not search_params:
                logger.error("Failed to extract search parameters from dealer page")
                return InventorySearchResult(
                    success=False,
                    cars=[],
                    totalResults=0,
                    currentPage=page_number,
                    totalPages=0,
                    hasNextPage=False,
                    processingTime=time.time() - start_time,
                    message="Failed to extract search parameters from dealer page"
                )
            
            # Now make the AJAX request to get the specific page
            ajax_url = "https://www.cargurus.com/Cars/searchPreflight.action"
            
            # Update headers for AJAX request
            self.session.headers.update({
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-device-memory': '8',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-full-version-list': '"Not)A;Brand";v="8.0.0.0", "Chromium";v="138.0.7204.188", "Google Chrome";v="138.0.7204.188"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-cg-client-id': 'site-cars',
                'x-requested-with': 'XMLHttpRequest',
                'referer': dealer_url
            })
            
            # Update search parameters for the specific page
            search_params['pageNumber'] = page_number
            
            logger.info(f"Making AJAX request to: {ajax_url}")
            logger.info(f"Parameters: {search_params}")
            
            # Make the AJAX request
            ajax_response = self.session.get(ajax_url, params=search_params, timeout=self.timeout)
            
            if ajax_response.status_code != 200:
                logger.error(f"AJAX request failed: HTTP {ajax_response.status_code}")
                return InventorySearchResult(
                    success=False,
                    cars=[],
                    totalResults=0,
                    currentPage=page_number,
                    totalPages=0,
                    hasNextPage=False,
                    processingTime=time.time() - start_time,
                    message=f"AJAX request failed: HTTP {ajax_response.status_code}"
                )
            
            # Extract cars from the AJAX response
            cars = self._extract_cars_from_ajax_response(ajax_response.text, dealer_entity_id)
            
            if cars:
                processing_time = time.time() - start_time
                logger.info(f"Successfully found {len(cars)} cars from AJAX response in {processing_time:.2f}s")
                
                # Get the total number of cars from the AJAX response (filtered total)
                total_cars = self._extract_total_cars_from_ajax_response(ajax_response.text)
                
                if total_cars > 0:
                    # Use the actual total cars for accurate pagination
                    # Based on testing, CarGurus shows 23 cars per page for dealer inventory
                    cars_per_page = 23  # CarGurus shows 23 cars per page for dealer inventory
                    total_pages = max(1, (total_cars + cars_per_page - 1) // cars_per_page)
                    has_next_page = page_number < total_pages
                    
                    logger.info(f"Total cars from dealer page: {total_cars}")
                    logger.info(f"Calculated total pages: {total_pages}")
                    logger.info(f"Has next page: {has_next_page}")
                    
                    return InventorySearchResult(
                        success=True,
                        cars=cars,
                        totalResults=total_cars,  # Use actual total from dealer page
                        currentPage=page_number,
                        totalPages=total_pages,
                        hasNextPage=has_next_page,
                        processingTime=processing_time,
                        message=f"Successfully scraped {len(cars)} cars from dealer page {page_number} (Total: {total_cars})"
                    )
                else:
                    # Fallback to estimation if we can't get the total
                    cars_per_page = 23  # CarGurus shows 23 cars per page for dealer inventory
                    estimated_total_cars = len(cars) * 2
                    estimated_total_pages = max(1, (estimated_total_cars + cars_per_page - 1) // cars_per_page)
                    has_next_page = len(cars) >= cars_per_page
                    
                    logger.warning("Could not extract total cars from dealer page, using estimation")
                    
                    return InventorySearchResult(
                        success=True,
                        cars=cars,
                        totalResults=len(cars),  # Show actual cars found
                        currentPage=page_number,
                        totalPages=estimated_total_pages,
                        hasNextPage=has_next_page,
                        processingTime=processing_time,
                        message=f"Successfully scraped {len(cars)} cars from dealer page {page_number} (estimated total)"
                    )
            else:
                logger.warning("No cars found in AJAX response")
                return InventorySearchResult(
                    success=False,
                    cars=[],
                    totalResults=0,
                    currentPage=page_number,
                    totalPages=0,
                    hasNextPage=False,
                    processingTime=time.time() - start_time,
                    message="No cars found in AJAX response"
                )
                        
        except Exception as e:
            logger.error(f"Unexpected error in dealer page scrape: {e}")
            import traceback
            traceback.print_exc()
            return InventorySearchResult(
                success=False,
                cars=[],
                totalResults=0,
                currentPage=page_number,
                totalPages=0,
                hasNextPage=False,
                processingTime=time.time() - start_time,
                message=f"Unexpected error: {str(e)}"
            )

    def _extract_cars_from_search_page(self, html_content: str, request: InventorySearchRequest) -> List[ScrapedCar]:
        """
        Extract car listings from the search page HTML.
        
        Args:
            html_content: HTML content of the search page
            request: Original search request
            
        Returns:
            List of ScrapedCar objects
        """
        cars = []
        
        try:
            # Use regex to find car listings in the HTML
            # Look for patterns that indicate car listings
            import re

            print(html_content)
            
            # Pattern to find car listing URLs
            listing_pattern = r'href="([^"]*inventorylisting[^"]*)"'
            listing_matches = re.findall(listing_pattern, html_content)
            
            # Also look for JSON data embedded in the page
            json_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
            json_match = re.search(json_pattern, html_content, re.DOTALL)
            
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    # Extract car data from JSON if available
                    cars.extend(self._extract_cars_from_json_data(json_data))
                except json.JSONDecodeError:
                    logger.warning("Failed to parse embedded JSON data")
            
            # If no cars found from JSON, try to extract from listing URLs
            if not cars and listing_matches:
                logger.info(f"Found {len(listing_matches)} potential listing URLs")
                
                # Limit to first 10 listings to avoid overwhelming the system
                for i, listing_url in enumerate(listing_matches[:10]):
                    try:
                        # Convert relative URLs to absolute URLs
                        if listing_url.startswith('/'):
                            listing_url = f"https://www.cargurus.com{listing_url}"
                        
                        # Scrape individual car
                        car = self.scrape_car(listing_url)
                        if car:
                            cars.append(car)
                            logger.info(f"Successfully scraped car {i+1}: {car.fullTitle}")
                        
                        # Add delay between requests to be respectful
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"Failed to scrape car from {listing_url}: {str(e)}")
                        continue
            
            logger.info(f"Extracted {len(cars)} cars from search page")
            return cars
            
        except Exception as e:
            logger.error(f"Error extracting cars from search page: {str(e)}")
            return cars

    def _extract_cars_from_json_data(self, json_data: dict) -> List[ScrapedCar]:
        """
        Extract car data from embedded JSON in the search page.
        
        Args:
            json_data: JSON data from the search page
            
        Returns:
            List of ScrapedCar objects
        """
        cars = []
        
        try:
            # Navigate through the JSON structure to find car listings
            # This structure may vary, so we'll try multiple paths
            
            # Common paths for car data in CarGurus JSON
            possible_paths = [
                ['searchResults', 'listings'],
                ['listings'],
                ['cars'],
                ['inventory', 'listings'],
                ['data', 'listings']
            ]
            
            listings = None
            for path in possible_paths:
                current = json_data
                try:
                    for key in path:
                        current = current[key]
                    listings = current
                    break
                except (KeyError, TypeError):
                    continue
            
            if listings and isinstance(listings, list):
                for listing in listings:
                    try:
                        car = self._extract_car_from_listing_json(listing)
                        if car:
                            cars.append(car)
                    except Exception as e:
                        logger.warning(f"Failed to extract car from listing JSON: {str(e)}")
                        continue
            
            return cars
            
        except Exception as e:
            logger.error(f"Error extracting cars from JSON data: {str(e)}")
            return cars

    def _extract_car_from_listing_json(self, listing: dict) -> Optional[ScrapedCar]:
        """
        Extract car data from a single listing JSON object.
        
        Args:
            listing: JSON object representing a car listing
            
        Returns:
            ScrapedCar object if successful, None otherwise
        """
        try:
            # Extract basic information
            make = listing.get('makeName', listing.get('make', 'Unknown'))
            model = listing.get('modelName', listing.get('model', 'Unknown'))
            year = listing.get('year', 0)
            price = listing.get('price', 0.0)
            
            # Construct full title
            full_title = f"{year} {make} {model}".strip()
            
            # Extract images
            images = []
            if 'images' in listing:
                for img in listing['images']:
                    if isinstance(img, dict) and 'url' in img:
                        images.append(img['url'])
                    elif isinstance(img, str):
                        images.append(img)
            
            # Extract description
            description = listing.get('description', 'No description available.')
            
            # Extract features
            features = []
            if 'features' in listing:
                features = listing['features']
            elif 'options' in listing:
                features = listing['options']
            
            # Extract stats
            stats = []
            if 'stats' in listing:
                for stat in listing['stats']:
                    if isinstance(stat, dict) and 'header' in stat and 'value' in stat:
                        stats.append(stat)
            
            # Create ScrapedCar object
            return ScrapedCar(
                make=make,
                model=model,
                year=year,
                price=price,
                description=description,
                features=features,
                stats=stats,
                images=images,
                originalUrl=listing.get('url', ''),
                fullTitle=full_title
            )
            
        except Exception as e:
            logger.warning(f"Error extracting car from listing JSON: {str(e)}")
            return None
    
    def _is_valid_cargurus_url(self, url: str) -> bool:
        """Validate that the URL is a valid CarGurus.com URL"""
        try:
            parsed = urlparse(url)
            # Check if it's a CarGurus domain
            if parsed.netloc not in ('www.cargurus.com', 'cargurus.com'):
                return False
            
            # Check if it's a car-related page (more flexible)
            car_indicators = [
                '/Cars/',
                '/inventorylisting/',
                '/listing',
                'cargurus.com'
            ]
            
            url_lower = url.lower()
            return any(indicator.lower() in url_lower for indicator in car_indicators)
            
        except Exception:
            return False
    
    def _extract_listing_id(self, url: str) -> Optional[str]:
        """Extract listing ID from CarGurus URL using multiple patterns"""
        try:
            # Pattern 1: listingId parameter (e.g., ?listingId=123456789)
            if 'listingId=' in url:
                start = url.find('listingId=') + len('listingId=')
                end = url.find('&', start)
                if end == -1:
                    end = url.find('#', start)
                if end == -1:
                    end = len(url)
                listing_id = url[start:end]
                if listing_id.isdigit():
                    return listing_id
            
            # Pattern 2: /listing=ID/ format (e.g., #listing=123456789/NONE/DEFAULT)
            if '/listing=' in url:
                start = url.find('/listing=') + len('/listing=')
                end = url.find('/', start)
                if end == -1:
                    end = len(url)
                listing_part = url[start:end]
                # Extract just the ID part before any slashes
                listing_id = listing_part.split('/')[0]
                if listing_id.isdigit():
                    return listing_id
            
            # Pattern 3: #listing=ID format (e.g., #listing=123456789/NONE/DEFAULT)
            if '#listing=' in url:
                start = url.find('#listing=') + len('#listing=')
                end = url.find('/', start)
                if end == -1:
                    end = len(url)
                listing_part = url[start:end]
                # Extract just the ID part before any slashes
                listing_id = listing_part.split('/')[0]
                if listing_id.isdigit():
                    return listing_id
            
            # Pattern 4: Extract from URL path (e.g., /Cars/l-123456789)
            # Look for patterns like /l-123456789 or similar
            import re
            path_patterns = [
                r'/l-(\d+)',  # /l-123456789
                r'/listing/(\d+)',  # /listing/123456789
                r'/inventorylisting/(\d+)',  # /inventorylisting/123456789
            ]
            
            for pattern in path_patterns:
                match = re.search(pattern, url)
                if match:
                    listing_id = match.group(1)
                    if listing_id.isdigit():
                        return listing_id
            
            # Pattern 5: Extract from query parameters (various formats)
            query_patterns = [
                r'[?&]id=(\d+)',
                r'[?&]listing=(\d+)',
                r'[?&]inventoryId=(\d+)',
            ]
            
            for pattern in query_patterns:
                match = re.search(pattern, url)
                if match:
                    listing_id = match.group(1)
                    if listing_id.isdigit():
                        return listing_id
            
            # Pattern 6: Look for any sequence of 6+ digits that might be a listing ID
            digit_pattern = r'(\d{6,})'
            matches = re.findall(digit_pattern, url)
            for match in matches:
                # Check if this looks like a listing ID (not a zip code, year, etc.)
                if len(match) >= 6 and not self._is_likely_not_listing_id(match, url):
                    return match
            
            logger.warning(f"Could not extract listing ID from URL: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting listing ID from {url}: {str(e)}")
            return None
    
    def _is_likely_not_listing_id(self, candidate: str, url: str) -> bool:
        """Check if a candidate ID is likely not a listing ID"""
        # Years are not listing IDs
        if len(candidate) == 4 and 1900 <= int(candidate) <= 2030:
            return True
        
        # Zip codes are not listing IDs
        if len(candidate) == 5 and url.find('zip=' + candidate) != -1:
            return True
        
        # Phone numbers are not listing IDs
        if len(candidate) == 10 and candidate.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')):
            return True
        
        return False
    
    def _fetch_json_data(self, listing_id: str) -> Optional[dict]:
        """
        Fetch JSON data from CarGurus API.
        
        Args:
            listing_id: The listing ID to fetch
            
        Returns:
            JSON data as dict, or None if failed
        """
        import time
        
        # Construct the API URL
        api_url = f"https://www.cargurus.com/Cars/detailListingJson.action"
        params = {
            'inventoryListing': listing_id,
            'inclusionType': 'DEFAULT',
            'pid': 'null',
            'sourceContext': 'carGurusHomePageModel',
            'isDAVE': 'true'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(api_url, params=params, timeout=self.timeout)
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        if 'listing' in json_data:
                            logger.info(f"Successfully fetched JSON data for listing {listing_id}")
                            return json_data
                        else:
                            logger.warning(f"Invalid JSON response structure for listing {listing_id}")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON for listing {listing_id}: {str(e)}")
                else:
                    logger.warning(f"HTTP {response.status_code} for listing {listing_id} (attempt {attempt + 1})")
                    
            except requests.Timeout:
                logger.warning(f"Timeout for listing {listing_id} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error fetching listing {listing_id} (attempt {attempt + 1}): {str(e)}")
            
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _extract_car_data_from_json(self, json_data: dict, url: str) -> Optional[ScrapedCar]:
        """
        Extract car data from CarGurus JSON response.
        
        Args:
            json_data: The JSON response from CarGurus API
            url: Original URL
            
        Returns:
            ScrapedCar object if successful, None otherwise
        """
        try:
            listing = json_data.get('listing', {})
            
            # Extract car information from autoEntityInfo for more accurate data
            auto_entity_info = listing.get('autoEntityInfo', {})
            
            # Extract year, make, model, and trim from autoEntityInfo
            year = auto_entity_info.get('year', listing.get('year', 0))
            make = auto_entity_info.get('make', listing.get('makeName', 'Unknown'))
            model = auto_entity_info.get('model', listing.get('modelName', 'Unknown'))
            
            # Try to get trim from multiple sources
            trim = auto_entity_info.get('trim', '')
            if not trim or trim.strip() == '':
                # Try to extract from listingTitleOnly first (most complete)
                listing_title = listing.get('listingTitleOnly', '')
                if listing_title:
                    # Extract the part after the model name
                    model_name = listing.get('modelName', '')
                    if model_name and model_name in listing_title:
                        # Find the part after the model name
                        parts = listing_title.split(model_name, 1)
                        if len(parts) > 1:
                            potential_trim = parts[1].strip()
                            if potential_trim:
                                trim = potential_trim
            if not trim or trim.strip() == '':
                # Fallback to trimName from listing
                trim = listing.get('trimName', '')
            
            # Construct the full title: Year Make Model Trim
            if trim and trim.strip():
                fullTitle = f"{year} {make} {model} {trim}".strip()
            else:
                fullTitle = f"{year} {make} {model}".strip()
            
            price = listing.get('price', 0.0)
            description = listing.get('description', 'No description available.')
            
            # Extract features from options and description
            features = self._extract_features_from_json(listing)
            
            # Extract stats information
            stats = self._extract_stats_from_json(listing)
            
            # Extract all images
            images = self._extract_images_from_json(listing)
            
            # Validate that we have at least basic information
            if not make or not model or year == 0:
                logger.warning(f"Insufficient car data extracted from JSON")
                return None
            
            logger.info(f"Extracted car title: {fullTitle}")
            
            return ScrapedCar(
                make=make,
                model=model,
                year=year,
                price=price,
                description=description,
                features=features,
                stats=stats,
                images=images,
                originalUrl=url,
                fullTitle=fullTitle  # Add the constructed title
            )
            
        except Exception as e:
            logger.error(f"Error extracting car data from JSON: {str(e)}")
            return None
    
    def _extract_features_from_json(self, listing: dict) -> List[str]:
        """Extract features from JSON data"""
        features = []
        
        # Add options from the listing
        options = listing.get('options', [])
        features.extend(options)
        
        # Extract features from description
        description = listing.get('description', '')
        if description:
            # Split description by common separators and extract features
            desc_parts = description.split('[!@@Additional Info@@!]')
            if len(desc_parts) > 1:
                additional_info = desc_parts[1]
                # Split by commas and clean up
                additional_features = [feature.strip() for feature in additional_info.split(',') if feature.strip()]
                features.extend(additional_features)
        
        # Add some basic specs if available
        if listing.get('localizedTransmission'):
            features.append(f"Transmission: {listing['localizedTransmission']}")
        if listing.get('localizedDriveTrain'):
            features.append(f"Drivetrain: {listing['localizedDriveTrain']}")
        if listing.get('localizedEngineDisplayName'):
            features.append(f"Engine: {listing['localizedEngineDisplayName']}")
        if listing.get('mileageString'):
            features.append(f"Mileage: {listing['mileageString']}")
        
        if not features:
            features.append("Features not available")
        
        return features
    
    def _extract_stats_from_json(self, listing: dict) -> List[dict]:
        """Extract stats information from listingDetailStatsSectionDto"""
        stats = []
        
        try:
            # Extract stats from listingDetailStatsSectionDto
            stats_section = listing.get('listingDetailStatsSectionDto', [])
            
            if not isinstance(stats_section, list):
                logger.warning("listingDetailStatsSectionDto is not a list")
                return stats
            
            for category in stats_section:
                if not isinstance(category, dict):
                    continue
                
                category_name = category.get('categoryName', '')
                items = category.get('items', [])
                options_list = category.get('optionsList', [])
                
                # Add category header if it has items
                if items and category_name:
                    stats.append({
                        'header': f"📋 {category_name}",
                        'value': f"{len(items)} items"
                    })
                
                # Add individual items
                if items:  # Check if items is not None
                    for item in items:
                        if isinstance(item, dict):
                            label = item.get('label', '')
                            display_value = item.get('displayValue', '')
                            if label and display_value:
                                stats.append({
                                    'header': label,
                                    'value': display_value
                                })
                
                # Add options if they exist
                if options_list and category_name and options_list is not None:
                    option_names = [opt.get('name', '') for opt in options_list if isinstance(opt, dict) and opt.get('name')]
                    if option_names:
                        stats.append({
                            'header': f"🔧 {category_name} Options",
                            'value': f"{len(option_names)} options"
                        })
                        # Add individual options
                        for option_name in option_names:
                            stats.append({
                                'header': "  • " + option_name,
                                'value': "✓"
                            })
            
            logger.info(f"Extracted {len(stats)} stats from listing")
            
        except Exception as e:
            logger.warning(f"Error extracting stats: {str(e)}")
            # Return empty list if there's an error
            stats = []
        
        return stats
    
    def _extract_images_from_json(self, listing: dict) -> List[str]:
        """Extract all images from JSON data"""
        images = []
        
        pictures = listing.get('pictures', [])
        for picture in pictures:
            # Use the main URL (1024x768) for best quality
            url = picture.get('url')
            if url and url not in images:
                images.append(url)
        
        # If no images found, add placeholder
        if not images:
            images.append("https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=800&h=600&fit=crop")
        
        return images 

    def _extract_cars_from_json_response(self, json_data: dict) -> List[ScrapedCar]:
        """
        Extract car listings from JSON response from CarGurus.
        
        Args:
            json_data: JSON data from the CarGurus search response
            
        Returns:
            List of ScrapedCar objects
        """
        cars = []
        
        try:
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
                    
                    # Look for car listing tiles using partial matching
                    is_listing_tile = False
                    matched_pattern = ""
                    
                    # Match any tile type that starts with LISTING_ and contains car data
                    if re.match(r'LISTING_.*', tile_type):
                        is_listing_tile = True
                        matched_pattern = "LISTING_.*"
                        logger.info(f"DEBUG: Tile {i+1} matched LISTING_.* pattern")
                    # Also check if it's a MERCH tile that might contain car data
                    elif tile_type == 'MERCH' and tile_data and any(key in tile_data for key in ['makeName', 'modelName', 'carYear']):
                        is_listing_tile = True
                        matched_pattern = "MERCH_WITH_CAR_DATA"
                        logger.info(f"DEBUG: Tile {i+1} matched MERCH pattern")
                    
                    logger.info(f"DEBUG: Tile {i+1} - is_listing_tile={is_listing_tile}, tile_data={bool(tile_data)}, tile_data_type={type(tile_data)}")
                    
                    if is_listing_tile and tile_data:
                        logger.info(f"Tile {i+1} matched pattern '{matched_pattern}' for type '{tile_type}'")
                        car_data = self._extract_car_from_json_tile(tile_data)
                        if car_data:
                            cars.append(car_data)
                            logger.info(f"Successfully extracted car: {car_data.make} {car_data.model} {car_data.year}")
                        else:
                            logger.warning(f"Failed to extract car data from tile {i+1}")
                    else:
                        logger.info(f"Skipping tile {i+1} - type: {tile_type}, is_listing_tile={is_listing_tile}, has_tile_data={bool(tile_data)}")
                        
                except Exception as e:
                    logger.warning(f"Error processing tile {i+1}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(cars)} cars from JSON response")
            return cars
            
        except Exception as e:
            logger.error(f"Error extracting cars from JSON response: {e}")
            return cars
    
    def _extract_car_from_json_tile(self, tile_data: dict) -> Optional[ScrapedCar]:
        """
        Extract car data from a JSON tile.
        
        Args:
            tile_data: Data from a single tile
            
        Returns:
            ScrapedCar object if successful, None otherwise
        """
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
            original_url = f"https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId={listing_id}&entitySelectingHelper.selectedEntity=m6#listing={listing_id}/NONE/DEFAULT" if listing_id else "https://www.cargurus.com/Cars"
            
            # Extract additional info
            mileage = tile_data.get('mileage', 0)
            mileage_string = tile_data.get('mileageString', '0')
            exterior_color = tile_data.get('exteriorColorName', 'Unknown')
            dealer_name = tile_data.get('dealerName', 'Unknown')
            seller_city = tile_data.get('sellerCity', '')
            seller_region = tile_data.get('sellerRegion', '')
            
            # Create ScrapedCar object
            logger.info(f"Creating ScrapedCar with: make={make}, model={model}, year={year}, price={price}")
            logger.info(f"Features count: {len(features)}, Images count: {len(images)}")
            
            try:
                car = ScrapedCar(
                    make=make,
                    model=model,
                    year=year,
                    price=price,
                    description=description,
                    features=features,
                    images=images,
                    originalUrl=original_url,
                    fullTitle=title,
                    scrapedAt=datetime.now()
                )
                
                logger.info(f"Successfully created ScrapedCar object: {make} {model} {year} - ${price}")
                return car
                
            except Exception as e:
                logger.error(f"Failed to create ScrapedCar object: {e}")
                logger.error(f"Data: make={make}, model={model}, year={year}, price={price}")
                logger.error(f"Features: {features}")
                logger.error(f"Images: {images}")
                return None
            
        except Exception as e:
            logger.warning(f"Error extracting car from JSON tile: {e}")
            return None 

    def _extract_cars_from_dealer_page(self, html_content: str) -> List[ScrapedCar]:
        """
        Extract car listings from the dealer page HTML content.
        This method parses the actual dealer page HTML to find car listings.
        """
        logger.info("=== EXTRACTING CARS FROM DEALER PAGE HTML ===")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            cars = []
            
            # Look for car listing elements on the dealer page
            # These might be in different formats depending on the page structure
            
            # Method 1: Look for listing cards/containers
            listing_containers = soup.find_all(['div', 'article'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['listing', 'card', 'tile', 'car']))
            
            if listing_containers:
                logger.info(f"Found {len(listing_containers)} potential listing containers")
                
                for i, container in enumerate(listing_containers[:50]):  # Limit to first 50 for testing
                    try:
                        car = self._extract_car_from_dealer_listing_container(container)
                        if car:
                            cars.append(car)
                            logger.info(f"Successfully extracted car {i+1}: {car.make} {car.model} {car.year}")
                    except Exception as e:
                        logger.warning(f"Error extracting car from container {i+1}: {e}")
                        continue
            
            # Method 2: Look for JSON data embedded in the page
            if not cars:
                logger.info("No cars found via containers, trying to extract from embedded JSON")
                cars = self._extract_cars_from_embedded_json(html_content)
            
            # Method 3: Look for specific HTML patterns
            if not cars:
                logger.info("No cars found via JSON, trying HTML pattern matching")
                cars = self._extract_cars_from_html_patterns(html_content)
            
            logger.info(f"Successfully extracted {len(cars)} cars from dealer page HTML")
            return cars
            
        except Exception as e:
            logger.error(f"Error extracting cars from dealer page HTML: {e}")
            return []

    def _extract_car_from_dealer_listing_container(self, container) -> Optional[ScrapedCar]:
        """
        Extract car data from a single listing container on the dealer page.
        """
        try:
            # Try to extract basic car information from the container
            make_elem = container.find(['span', 'div', 'h3'], string=re.compile(r'\b[A-Z][a-z]+\b'))
            model_elem = container.find(['span', 'div', 'h3'], string=re.compile(r'\b[A-Z][a-z0-9\s\-]+\b'))
            year_elem = container.find(['span', 'div'], string=re.compile(r'\b(19|20)\d{2}\b'))
            price_elem = container.find(['span', 'div'], string=re.compile(r'\$[\d,]+'))
            
            if make_elem and model_elem and year_elem:
                make = make_elem.get_text(strip=True)
                model = model_elem.get_text(strip=True)
                year = int(year_elem.get_text(strip=True))
                price = 0
                
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'\$([\d,]+)', price_text)
                    if price_match:
                        price = int(price_match.group(1).replace(',', ''))
                
                # Create a basic ScrapedCar object
                car = ScrapedCar(
                    make=make,
                    model=model,
                    year=year,
                    price=price,
                    url="",  # We'll need to extract this
                    features=[],
                    images=[],
                    mileage=0,
                    color="",
                    transmission="",
                    drivetrain="",
                    fuel_type="",
                    engine="",
                    vin="",
                    stock_number=""
                )
                
                return car
                
        except Exception as e:
            logger.warning(f"Error extracting car from container: {e}")
            
        return None

    def _extract_cars_from_embedded_json(self, html_content: str) -> List[ScrapedCar]:
        """
        Try to extract car data from JSON embedded in the HTML page.
        """
        try:
            # Look for JSON data in script tags
            json_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
                r'window\.cgData\s*=\s*({.*?});',
                r'var\s+listingData\s*=\s*(\[.*?\]);'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                if matches:
                    try:
                        json_data = json.loads(matches[0])
                        logger.info(f"Found embedded JSON data with keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Array'}")
                        
                        # Try to extract cars from the JSON
                        cars = self._extract_cars_from_json_response(json_data)
                        if cars:
                            return cars
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.warning(f"Error extracting from embedded JSON: {e}")
            
        return []

    def _extract_cars_from_html_patterns(self, html_content: str) -> List[ScrapedCar]:
        """
        Try to extract car data using HTML pattern matching.
        """
        cars = []
        
        try:
            # Look for common car listing patterns in HTML
            # This is a fallback method when other methods fail
            
            # Pattern 1: Look for make/model/year combinations
            car_pattern = re.compile(r'<[^>]*>([^<]*?)\s+([^<]*?)\s+((?:19|20)\d{2})[^<]*</[^>]*>', re.IGNORECASE)
            matches = car_pattern.findall(html_content)
            
            for match in matches[:20]:  # Limit results
                make, model, year = match
                if make.strip() and model.strip() and year.strip():
                    try:
                        car = ScrapedCar(
                            make=make.strip(),
                            model=model.strip(),
                            year=int(year.strip()),
                            price=0,
                            url="",
                            features=[],
                            images=[],
                            mileage=0,
                            color="",
                            transmission="",
                            drivetrain="",
                            fuel_type="",
                            engine="",
                            vin="",
                            stock_number=""
                        )
                        cars.append(car)
                    except ValueError:
                        continue
                        
        except Exception as e:
            logger.warning(f"Error extracting from HTML patterns: {e}")
            
        return cars 

    def _extract_search_params_from_dealer_page(self, html_content: str, dealer_entity_id: str, inventory_type: str = "ALL") -> Optional[dict]:
        """
        Extract search parameters from the dealer page HTML.
        These parameters are needed for the AJAX pagination requests.
        
        Args:
            html_content: HTML content of the dealer page
            dealer_entity_id: Dealer entity ID
            inventory_type: Type of inventory to search (ALL, NEW, USED)
        """
        try:
            # Look for search parameters in the HTML
            # These might be in script tags, data attributes, or form elements
            
            # Pattern 1: Look for searchId in script tags
            search_id_pattern = r'searchId["\']?\s*[:=]\s*["\']([^"\']+)["\']'
            search_id_match = re.search(search_id_pattern, html_content)
            search_id = search_id_match.group(1) if search_id_match else None
            
            # Pattern 2: Look for pageReceipt in script tags
            page_receipt_pattern = r'pageReceipt["\']?\s*[:=]\s*["\']([^"\']+)["\']'
            page_receipt_match = re.search(page_receipt_pattern, html_content)
            page_receipt = page_receipt_match.group(1) if page_receipt_match else None
            
            # Map inventory type to CarGurus newUsed parameter (single value format)
            new_used_mapping = {
                "ALL": "",  # All types: New Certified, New, Used
                "NEW": 1,        # New only
                "USED": 2,       # Used only
                "NEW_CERTIFIED": 8  # New Certified only
            }
            new_used_value = new_used_mapping.get(inventory_type.upper(), "")
            print(f"New Used Value: {new_used_value}")
            
            # Build the search parameters based on the Node.js fetch example
            search_params = {
                'searchId': search_id or 'f946015c-5531-4f6d-9c51-c34defd5256a',  # Fallback
                'distance': '100',
                'entitySelectingHelper.selectedEntity': f'sp{dealer_entity_id}',
                'sourceContext': 'untrackedWithinSite_false_0',
                'sortDir': 'ASC',
                'sortType': 'BEST_MATCH',
                'srpVariation': 'DEALER_INVENTORY',
                'newUsed': new_used_value,  # Add the newUsed parameter for inventory filtering
                'isDeliveryEnabled': 'true',
                'nonShippableBaseline': '0',
                'filtersModified': 'true'
            }
            
            # Add pageReceipt if found
            if page_receipt:
                search_params['pageReceipt'] = page_receipt
            
            logger.info(f"Extracted search parameters: {search_params}")
            return search_params
            
        except Exception as e:
            logger.error(f"Error extracting search parameters: {e}")
            return None

    def _extract_cars_from_ajax_response(self, html_content: str, dealer_entity_id: str = "") -> List[ScrapedCar]:
        """
        Extract car listings from the AJAX response.
        The AJAX response contains JSON data with car listings.
        """
        logger.info("=== EXTRACTING CARS FROM AJAX RESPONSE ===")
        
        try:
            # The AJAX response is actually JSON, not HTML
            # Try to parse it as JSON first
            try:
                json_data = json.loads(html_content)
                logger.info(f"Successfully parsed JSON response with keys: {list(json_data.keys())}")
                
                # Extract cars from the JSON data
                cars = self._extract_cars_from_ajax_json(json_data, dealer_entity_id)
                if cars:
                    logger.info(f"Successfully extracted {len(cars)} cars from JSON response")
                    return cars
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse response as JSON: {e}")
                # Fall back to HTML parsing if JSON fails
                pass
            
            # Fallback: Try HTML parsing (though this shouldn't be needed)
            soup = BeautifulSoup(html_content, 'html.parser')
            cars = []
            
            # Method 1: Look for car listing elements in the AJAX response
            listing_containers = soup.find_all(['div', 'article'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['listing', 'card', 'tile', 'car', 'result']))
            
            if listing_containers:
                logger.info(f"Found {len(listing_containers)} potential listing containers in AJAX response")
                
                for i, container in enumerate(listing_containers):
                    try:
                        car = self._extract_car_from_ajax_listing_container(container)
                        if car:
                            cars.append(car)
                            logger.info(f"Successfully extracted car {i+1}: {car.make} {car.model} {car.year}")
                    except Exception as e:
                        logger.warning(f"Error extracting car from AJAX container {i+1}: {e}")
                        continue
            
            # Method 2: Look for JSON data in the AJAX response
            if not cars:
                logger.info("No cars found via containers, trying to extract from embedded JSON in AJAX response")
                cars = self._extract_cars_from_embedded_json(html_content)
            
            # Method 3: Look for specific HTML patterns in AJAX response
            if not cars:
                logger.info("No cars found via JSON, trying HTML pattern matching in AJAX response")
                cars = self._extract_cars_from_html_patterns(html_content)
            
            logger.info(f"Successfully extracted {len(cars)} cars from AJAX response")
            return cars
            
        except Exception as e:
            logger.error(f"Error extracting cars from AJAX response: {e}")
            return []

    def _extract_cars_from_ajax_json(self, json_data: dict, dealer_entity_id: str = "") -> List[ScrapedCar]:
        """
        Extract car listings from the AJAX JSON response.
        The JSON contains a 'tiles' array with car listing data.
        """
        cars = []
        
        try:
            # The JSON response has a 'tiles' array
            tiles = json_data.get('tiles', [])
            logger.info(f"Found {len(tiles)} tiles in JSON response")
            
            for i, tile in enumerate(tiles):
                try:
                    # Check if this is a car listing tile
                    if tile.get('type') == 'LISTING_USED_STANDARD' or tile.get('type') == 'LISTING_NEW_STANDARD':
                        car_data = tile.get('data', {})
                        tile_type = tile.get('type', '')  # Pass the tile type!
                        car = self._extract_car_from_ajax_tile_data(car_data, dealer_entity_id, tile_type)
                        if car:
                            cars.append(car)
                            logger.info(f"Successfully extracted car {i+1}: {car.make} {car.model} {car.year}")
                    elif tile.get('type') == 'MERCH':
                        # Skip merchandise/advertisement tiles
                        logger.debug(f"Skipping MERCH tile {i}")
                        continue
                    else:
                        logger.debug(f"Unknown tile type: {tile.get('type')}")
                        
                except Exception as e:
                    logger.warning(f"Error extracting car from tile {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(cars)} cars from JSON tiles")
            return cars
            
        except Exception as e:
            logger.error(f"Error extracting cars from AJAX JSON: {e}")
            return []

    def _extract_car_from_ajax_tile_data(self, car_data: dict, dealer_entity_id: str = "", tile_type: str = "") -> Optional[ScrapedCar]:
        """
        Extract car data from a single tile in the AJAX JSON response.
        """
        try:
            # Extract basic car information
            make = car_data.get('makeName', '')
            model = car_data.get('modelName', '')
            year = car_data.get('carYear', 0)
            price = car_data.get('price', 0.0)
            
            # Extract listing ID for URL construction
            listing_id = car_data.get('id', '')
            
            # Extract description/title
            description = car_data.get('listingTitle', '')
            if not description:
                description = f"{year} {make} {model}"
            
            # Extract features from options
            features = car_data.get('options', [])
            
            # Extract stats
            stats = []

            # Add condition based on tile type (CRITICAL FIX!)
            if tile_type == 'LISTING_NEW_STANDARD':
                stats.append({"header": "Condition", "value": "New"})
            elif tile_type == 'LISTING_USED_STANDARD':
                stats.append({"header": "Condition", "value": "Used"})
            mileage = car_data.get('mileageString', '')
            if mileage:
                stats.append({"header": "Mileage", "value": mileage})
            
            transmission = car_data.get('localizedTransmission', '')
            if transmission:
                stats.append({"header": "Transmission", "value": transmission})
            
            drivetrain = car_data.get('localizedDriveTrain', '')
            if drivetrain:
                stats.append({"header": "Drivetrain", "value": drivetrain})
            
            fuel_type = car_data.get('localizedFuelType', '')
            if fuel_type:
                stats.append({"header": "Fuel Type", "value": fuel_type})
            
            engine = car_data.get('localizedEngineDisplayName', '')
            if engine:
                stats.append({"header": "Engine", "value": engine})
            
            # Extract images
            images = []
            original_picture = car_data.get('originalPictureData', {})
            if original_picture and original_picture.get('url'):
                images.append(original_picture['url'])
            
            # Extract VIN and stock number
            vin = car_data.get('vin', '')
            stock_number = car_data.get('stockNumber', '')
            
            # Construct the full title
            trim = car_data.get('trimName', '')
            if trim and trim.strip():
                full_title = f"{year} {make} {model} {trim}".strip()
            else:
                full_title = f"{year} {make} {model}".strip()
            
            # Construct the original CarGurus URL
            original_url = ""
            if listing_id and dealer_entity_id:
                original_url = f"https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId={listing_id}&entitySelectingHelper.selectedEntity=sp{dealer_entity_id}#listing={listing_id}/NONE/DEFAULT"
            elif listing_id:
                # Fallback URL without dealer entity if not provided
                original_url = f"https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId={listing_id}#listing={listing_id}/NONE/DEFAULT"
            
            # Validate that we have at least basic information
            if not make or not model or year == 0:
                logger.warning(f"Insufficient car data in tile: make={make}, model={model}, year={year}")
                return None
            
            logger.info(f"Extracted car: {full_title} - ${price:,} - URL: {original_url}")
            
            return ScrapedCar(
                make=make,
                model=model,
                year=year,
                price=price,
                description=description,
                features=features,
                stats=stats,
                images=images,
                originalUrl=original_url,
                fullTitle=full_title
            )
                
        except Exception as e:
            logger.warning(f"Error extracting car from tile data: {e}")
            
        return None 

    def _extract_car_from_ajax_listing_container(self, container) -> Optional[ScrapedCar]:
        """
        Extract car data from a single listing container in the AJAX response.
        This should be more reliable than the main page extraction.
        """
        try:
            # Try to extract basic car information from the container
            # Look for more specific selectors that might be used in AJAX responses
            
            # Look for title/name elements
            title_elem = container.find(['h3', 'h4', 'h5', 'div'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['title', 'name', 'heading']))
            
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                # Parse year, make, model from title
                car_info = self._parse_car_title(title_text)
                if car_info:
                    make, model, year = car_info
                    
                    # Look for price
                    price_elem = container.find(['span', 'div'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['price', 'cost']))
                    price = 0
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price_match = re.search(r'\$([\d,]+)', price_text)
                        if price_match:
                            price = int(price_match.group(1).replace(',', ''))
                    
                    # Look for description
                    desc_elem = container.find(['p', 'div'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['description', 'desc', 'summary']))
                    description = desc_elem.get_text(strip=True) if desc_elem else "No description available."
                    
                    # Look for images
                    img_elem = container.find('img')
                    images = [img_elem.get('src')] if img_elem and img_elem.get('src') else []
                    
                    # Create the car object
                    car = ScrapedCar(
                        make=make,
                        model=model,
                        year=year,
                        price=price,
                        description=description,
                        features=[],
                        stats=[],
                        images=images,
                        originalUrl="",  # We'll need to extract this
                        fullTitle=f"{year} {make} {model}"
                    )
                    
                    return car
            
            # Fallback: Try the same method as the main page
            return self._extract_car_from_dealer_listing_container(container)
                
        except Exception as e:
            logger.warning(f"Error extracting car from AJAX container: {e}")
            
        return None

    def _parse_car_title(self, title_text: str) -> Optional[tuple]:
        """
        Parse year, make, and model from a car title string.
        """
        try:
            # Pattern: "2022 Toyota Camry LE" or "2022 Toyota Camry"
            pattern = r'(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9\s\-]+)'
            match = re.search(pattern, title_text)
            
            if match:
                year = int(match.group(1))
                make = match.group(2).strip()
                model = match.group(3).strip()
                
                # Validate year
                if 1900 <= year <= 2030:
                    return (make, model, year)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing car title '{title_text}': {e}")
            return None

    def _extract_pagination_info_from_ajax_response(self, html_content: str) -> dict:
        """
        Extract pagination information from the AJAX response.
        """
        try:
            # Since the AJAX response is JSON, try to parse it first
            try:
                json_data = json.loads(html_content)
                # Look for pagination info in the JSON
                page_number = json_data.get('pageNumber', 1)
                # We can't determine total pages from this response, but we can check if there are more tiles
                tiles = json_data.get('tiles', [])
                has_next = len(tiles) > 0  # If we got tiles, there might be more pages
                
                return {
                    'totalResults': 0,  # We can't determine this from this response
                    'totalPages': 0,    # We can't determine this from this response
                    'hasNextPage': has_next
                }
            except json.JSONDecodeError:
                pass
            
            # Fallback: Look for pagination information in HTML (if response is HTML)
            # Pattern 1: Look for pagination JSON
            pagination_pattern = r'pagination["\']?\s*[:=]\s*({[^}]+})'
            pagination_match = re.search(pagination_pattern, html_content)
            
            if pagination_match:
                try:
                    pagination_data = json.loads(pagination_match.group(1))
                    return {
                        'totalResults': pagination_data.get('totalResults', 0),
                        'totalPages': pagination_data.get('totalPages', 1),
                        'hasNextPage': pagination_data.get('hasNextPage', False)
                    }
                except json.JSONDecodeError:
                    pass
            
            # Pattern 2: Look for pagination in HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for pagination elements
            pagination_elem = soup.find(['div', 'nav'], class_=lambda x: x and 'pagination' in x.lower())
            
            if pagination_elem:
                # Count page numbers
                page_numbers = pagination_elem.find_all(['a', 'span'], string=re.compile(r'\d+'))
                total_pages = len(page_numbers) if page_numbers else 1
                
                # Check for next button
                next_button = pagination_elem.find(['a', 'button'], string=re.compile(r'next|>', re.I))
                has_next = next_button is not None
                
                return {
                    'totalResults': 0,  # We can't determine this from HTML
                    'totalPages': total_pages,
                    'hasNextPage': has_next
                }
            
            # Default values
            return {
                'totalResults': 0,
                'totalPages': 1,
                'hasNextPage': False
            }
            
        except Exception as e:
            logger.warning(f"Error extracting pagination info: {e}")
            return {
                'totalResults': 0,
                'totalPages': 1,
                'hasNextPage': False
            }

    def _extract_total_cars_from_dealer_page(self, html_content: str, dealer_entity_id: str) -> int:
        """
        Extract the total number of cars from the dealer page H1 tag.
        
        Args:
            html_content: HTML content of the dealer page
            dealer_entity_id: Dealer entity ID for logging
            
        Returns:
            Total number of cars as integer, or 0 if not found
        """
        try:
            # Look for the H1 tag with class="dealerName" that contains the total cars
            # Pattern: <h1 class="dealerName">... - 163 Cars for Sale</h1>
            dealer_name_pattern = r'<h1[^>]*class="dealerName"[^>]*>.*?-\s*(\d+)\s+Cars?\s+for\s+Sale\s*</h1>'
            match = re.search(dealer_name_pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            if match:
                total_cars = int(match.group(1))
                logger.info(f"Extracted total cars from dealer page: {total_cars}")
                return total_cars
            
            # Alternative pattern: Look for "X Cars for Sale" anywhere in the page
            cars_pattern = r'(\d+)\s+Cars?\s+for\s+Sale'
            match = re.search(cars_pattern, html_content, re.IGNORECASE)
            
            if match:
                total_cars = int(match.group(1))
                logger.info(f"Extracted total cars using alternative pattern: {total_cars}")
                return total_cars
            
            # Try parsing with BeautifulSoup as fallback
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for H1 with dealerName class
            dealer_h1 = soup.find('h1', class_='dealerName')
            if dealer_h1:
                h1_text = dealer_h1.get_text()
                # Extract number from text like "Asheboro Chrysler Dodge Jeep Ram - 163 Cars for Sale"
                cars_match = re.search(r'(\d+)\s+Cars?\s+for\s+Sale', h1_text, re.IGNORECASE)
                if cars_match:
                    total_cars = int(cars_match.group(1))
                    logger.info(f"Extracted total cars using BeautifulSoup: {total_cars}")
                    return total_cars
            
            logger.warning(f"Could not extract total cars from dealer page for dealer {dealer_entity_id}")
            return 0
            
        except Exception as e:
            logger.error(f"Error extracting total cars from dealer page: {e}")
            return 0

    def _extract_total_cars_from_ajax_response(self, ajax_response_text: str) -> int:
        """
        Extract the total number of cars from the AJAX response JSON.
        
        Args:
            ajax_response_text: JSON response text from the AJAX request
            
        Returns:
            Total number of cars as integer, or 0 if not found
        """
        try:
            # Try to parse the AJAX response as JSON
            json_data = json.loads(ajax_response_text)
            
            # Look for totalListings in the JSON response
            # Based on the curl response, it should be at the root level
            total_listings = json_data.get('totalListings', 0)
            
            if total_listings > 0:
                logger.info(f"Extracted total cars from AJAX response: {total_listings}")
                return total_listings
            
            # Fallback: try to find it in other common locations
            if 'srpTrackingData' in json_data:
                srp_data = json_data['srpTrackingData']
                if 'defaultSRPListingCount' in srp_data:
                    count_data = srp_data['defaultSRPListingCount']
                    total_listings = count_data.get('totalListings', 0)
                    if total_listings > 0:
                        logger.info(f"Extracted total cars from srpTrackingData: {total_listings}")
                        return total_listings
            
            logger.warning("Could not extract total cars from AJAX response")
            return 0
            
        except json.JSONDecodeError:
            logger.warning("AJAX response is not valid JSON, cannot extract total cars")
            return 0
        except Exception as e:
            logger.error(f"Error extracting total cars from AJAX response: {e}")
            return 0 