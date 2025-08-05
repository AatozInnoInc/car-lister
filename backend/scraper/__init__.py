"""
Car Lister Scraper Package

This package contains the scraping functionality for the Car Lister PWA.
It provides professional web scraping capabilities for CarGurus.com with
robust error handling, retry logic, and clean architecture patterns.
"""

from .cargurus_scraper import CarGurusScraper
from .models import ScrapedCar, ScrapingResult

__all__ = ['CarGurusScraper', 'ScrapedCar', 'ScrapingResult']
__version__ = '1.0.0' 