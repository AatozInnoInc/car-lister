/**
 * Car Lister API - Google Apps Script Integration
 * 
 * This script demonstrates how to integrate with the Car Lister API from Google Apps Script.
 * It can be used in Google Sheets to fetch car data and populate spreadsheets.
 * 
 * API Base URL: https://car-lister-api.onrender.com
 * 
 * @author Car Lister Team
 * @version 1.0.0
 */

// Configuration
const API_BASE_URL = 'https://car-lister-api.onrender.com';
const API_TIMEOUT = 30000; // 30 seconds

/**
 * Test the API connection
 * @returns {Object} API health status
 */
function testApiConnection() {
  try {
    const response = UrlFetchApp.fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      muteHttpExceptions: true,
      timeout: API_TIMEOUT
    });
    
    const data = JSON.parse(response.getContentText());
    
    if (response.getResponseCode() === 200) {
      Logger.log('API Connection Test: SUCCESS');
      Logger.log(`Status: ${data.status}`);
      Logger.log(`Service: ${data.service}`);
      Logger.log(`Version: ${data.version}`);
      return data;
    } else {
      Logger.log('API Connection Test: FAILED');
      Logger.log(`HTTP Code: ${response.getResponseCode()}`);
      Logger.log(`Response: ${response.getContentText()}`);
      return null;
    }
  } catch (error) {
    Logger.log('API Connection Test: ERROR');
    Logger.log(`Error: ${error.toString()}`);
    return null;
  }
}

/**
 * Scrape a single car from CarGurus URL
 * @param {string} carGurusUrl - The CarGurus.com URL to scrape
 * @returns {Object|null} Scraped car data or null if failed
 */
function scrapeCar(carGurusUrl) {
  try {
    const payload = {
      url: carGurusUrl
    };
    
    const response = UrlFetchApp.fetch(`${API_BASE_URL}/api/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true,
      timeout: API_TIMEOUT
    });
    
    const data = JSON.parse(response.getContentText());
    
    if (response.getResponseCode() === 200 && data.success) {
      Logger.log(`Successfully scraped: ${data.data.fullTitle}`);
      return data.data;
    } else {
      Logger.log(`Failed to scrape car: ${data.error || 'Unknown error'}`);
      return null;
    }
  } catch (error) {
    Logger.log(`Error scraping car: ${error.toString()}`);
    return null;
  }
}

/**
 * Search for cars in inventory
 * @param {string} zipCode - 5-digit ZIP code
 * @param {number} distance - Search radius in miles (1-500)
 * @param {number} pageNumber - Page number (1-based)
 * @param {string} newUsed - "NEW", "USED", or "ALL"
 * @returns {Object|null} Search results or null if failed
 */
function searchInventory(zipCode, distance = 50, pageNumber = 1, newUsed = "USED") {
  try {
    const payload = {
      zip: zipCode,
      distance: distance,
      pageNumber: pageNumber,
      srpVariation: "DEALER_INVENTORY",
      newUsed: newUsed
    };
    
    const response = UrlFetchApp.fetch(`${API_BASE_URL}/api/inventory/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true,
      timeout: API_TIMEOUT
    });
    
    const data = JSON.parse(response.getContentText());
    
    if (response.getResponseCode() === 200 && data.success) {
      Logger.log(`Found ${data.cars.length} cars in search`);
      Logger.log(`Total results: ${data.totalResults}`);
      Logger.log(`Processing time: ${data.processingTime}s`);
      return data;
    } else {
      Logger.log(`Search failed: ${data.errorMessage || 'Unknown error'}`);
      return null;
    }
  } catch (error) {
    Logger.log(`Error searching inventory: ${error.toString()}`);
    return null;
  }
}

/**
 * Scrape dealer inventory
 * @param {string} dealerEntityId - Dealer's entity ID from CarGurus
 * @param {string} dealerName - Dealer's business name
 * @param {string} dealerUrl - Full CarGurus dealer page URL
 * @param {number} pageNumber - Page number (1-based)
 * @returns {Object|null} Dealer inventory or null if failed
 */
function scrapeDealerInventory(dealerEntityId, dealerName, dealerUrl, pageNumber = 1) {
  try {
    const payload = {
      dealerEntityId: dealerEntityId,
      dealerName: dealerName,
      dealerUrl: dealerUrl,
      pageNumber: pageNumber
    };
    
    const response = UrlFetchApp.fetch(`${API_BASE_URL}/api/dealer/inventory`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true,
      timeout: API_TIMEOUT
    });
    
    const data = JSON.parse(response.getContentText());
    
    if (response.getResponseCode() === 200 && data.success) {
      Logger.log(`Successfully scraped dealer inventory: ${data.cars.length} cars`);
      Logger.log(`Total cars: ${data.totalResults}`);
      Logger.log(`Total pages: ${data.totalPages}`);
      Logger.log(`Has next page: ${data.hasNextPage}`);
      return data;
    } else {
      Logger.log(`Dealer inventory scrape failed: ${data.errorMessage || 'Unknown error'}`);
      return null;
    }
  } catch (error) {
    Logger.log(`Error scraping dealer inventory: ${error.toString()}`);
    return null;
  }
}

/**
 * Populate Google Sheet with scraped car data
 * @param {Array} cars - Array of car objects
 * @param {string} sheetName - Name of the sheet to populate
 */
function populateSheetWithCars(cars, sheetName = 'Car Data') {
  try {
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = spreadsheet.getSheetByName(sheetName);
    
    // Create sheet if it doesn't exist
    if (!sheet) {
      sheet = spreadsheet.insertSheet(sheetName);
    }
    
    // Clear existing data
    sheet.clear();
    
    // Define headers
    const headers = [
      'Full Title',
      'Make',
      'Model', 
      'Year',
      'Price',
      'Description',
      'Features',
      'Mileage',
      'Transmission',
      'Drivetrain',
      'Fuel Type',
      'Engine',
      'Images',
      'Original URL',
      'Scraped At'
    ];
    
    // Set headers
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    // Format headers
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    sheet.getRange(1, 1, 1, headers.length).setBackground('#4285f4');
    sheet.getRange(1, 1, 1, headers.length).setFontColor('white');
    
    if (cars && cars.length > 0) {
      const rows = cars.map(car => {
        // Extract stats
        const mileage = car.stats?.find(stat => stat.header === 'Mileage')?.value || '';
        const transmission = car.stats?.find(stat => stat.header === 'Transmission')?.value || '';
        const drivetrain = car.stats?.find(stat => stat.header === 'Drivetrain')?.value || '';
        const fuelType = car.stats?.find(stat => stat.header === 'Fuel Type')?.value || '';
        const engine = car.stats?.find(stat => stat.header === 'Engine')?.value || '';
        
        return [
          car.fullTitle || '',
          car.make || '',
          car.model || '',
          car.year || '',
          car.price || 0,
          car.description || '',
          car.features?.join(', ') || '',
          mileage,
          transmission,
          drivetrain,
          fuelType,
          engine,
          car.images?.join(', ') || '',
          car.originalUrl || '',
          car.scrapedAt || ''
        ];
      });
      
      // Set data
      sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
      
      // Auto-resize columns
      sheet.autoResizeColumns(1, headers.length);
      
      Logger.log(`Successfully populated sheet with ${cars.length} cars`);
    } else {
      Logger.log('No cars to populate');
    }
    
  } catch (error) {
    Logger.log(`Error populating sheet: ${error.toString()}`);
  }
}

/**
 * Example function: Search for cars and populate sheet
 * This is a complete example that can be run directly
 */
function exampleSearchAndPopulate() {
  // Test API connection first
  const health = testApiConnection();
  if (!health) {
    Logger.log('Cannot proceed - API is not available');
    return;
  }
  
  // Search for cars in Beverly Hills area
  const searchResults = searchInventory('90210', 25, 1, 'USED');
  
  if (searchResults && searchResults.cars) {
    // Populate sheet with results
    populateSheetWithCars(searchResults.cars, 'Beverly Hills Cars');
    
    // Log summary
    Logger.log(`=== SEARCH SUMMARY ===`);
    Logger.log(`Location: 90210 (Beverly Hills)`);
    Logger.log(`Distance: 25 miles`);
    Logger.log(`Cars found: ${searchResults.cars.length}`);
    Logger.log(`Total available: ${searchResults.totalResults}`);
    Logger.log(`Processing time: ${searchResults.processingTime}s`);
    Logger.log(`Sheet populated: 'Beverly Hills Cars'`);
  } else {
    Logger.log('Search failed - no data to populate');
  }
}

/**
 * Example function: Scrape specific dealer inventory
 */
function exampleDealerInventory() {
  // Example dealer data (replace with actual dealer info)
  const dealerEntityId = '317131';
  const dealerName = 'ABC Motors';
  const dealerUrl = 'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?entitySelectingHelper.selectedEntity=sp317131';
  
  // Scrape first page of dealer inventory
  const dealerResults = scrapeDealerInventory(dealerEntityId, dealerName, dealerUrl, 1);
  
  if (dealerResults && dealerResults.cars) {
    // Populate sheet with dealer inventory
    populateSheetWithCars(dealerResults.cars, `${dealerName} Inventory`);
    
    // Log summary
    Logger.log(`=== DEALER INVENTORY SUMMARY ===`);
    Logger.log(`Dealer: ${dealerName}`);
    Logger.log(`Cars on page 1: ${dealerResults.cars.length}`);
    Logger.log(`Total dealer cars: ${dealerResults.totalResults}`);
    Logger.log(`Total pages: ${dealerResults.totalPages}`);
    Logger.log(`Has more pages: ${dealerResults.hasNextPage}`);
    Logger.log(`Processing time: ${dealerResults.processingTime}s`);
    Logger.log(`Sheet populated: '${dealerName} Inventory'`);
  } else {
    Logger.log('Dealer inventory scrape failed');
  }
}

/**
 * Example function: Scrape individual car
 */
function exampleScrapeIndividualCar() {
  // Example CarGurus URL (replace with actual URL)
  const carUrl = 'https://www.cargurus.com/Cars/inventorylisting/vdp.action?listingId=123456789&entitySelectingHelper.selectedEntity=m6#listing=123456789/NONE/DEFAULT';
  
  const car = scrapeCar(carUrl);
  
  if (car) {
    // Populate sheet with single car
    populateSheetWithCars([car], 'Individual Car');
    
    // Log car details
    Logger.log(`=== CAR DETAILS ===`);
    Logger.log(`Title: ${car.fullTitle}`);
    Logger.log(`Price: $${car.price.toLocaleString()}`);
    Logger.log(`Features: ${car.features.length}`);
    Logger.log(`Images: ${car.images.length}`);
    Logger.log(`Stats: ${car.stats.length}`);
    Logger.log(`Sheet populated: 'Individual Car'`);
  } else {
    Logger.log('Failed to scrape individual car');
  }
}

/**
 * Utility function: Get all cars from multiple pages
 * @param {string} zipCode - ZIP code for search
 * @param {number} distance - Search distance
 * @param {number} maxPages - Maximum pages to fetch
 * @returns {Array} Combined array of all cars
 */
function getAllCarsFromMultiplePages(zipCode, distance = 50, maxPages = 3) {
  const allCars = [];
  
  for (let page = 1; page <= maxPages; page++) {
    Logger.log(`Fetching page ${page}...`);
    
    const results = searchInventory(zipCode, distance, page, 'USED');
    
    if (results && results.cars) {
      allCars.push(...results.cars);
      Logger.log(`Added ${results.cars.length} cars from page ${page}`);
      
      // Check if we've reached the end
      if (page >= results.totalPages) {
        Logger.log(`Reached last page (${results.totalPages})`);
        break;
      }
      
      // Add delay between requests to be respectful
      Utilities.sleep(1000);
    } else {
      Logger.log(`Failed to fetch page ${page}`);
      break;
    }
  }
  
  Logger.log(`Total cars collected: ${allCars.length}`);
  return allCars;
}

/**
 * Example function: Get comprehensive car data
 */
function exampleComprehensiveSearch() {
  // Get cars from multiple pages
  const allCars = getAllCarsFromMultiplePages('90210', 25, 3);
  
  if (allCars.length > 0) {
    // Populate sheet with all cars
    populateSheetWithCars(allCars, 'Comprehensive Search');
    
    // Create summary sheet
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    let summarySheet = spreadsheet.getSheetByName('Search Summary');
    
    if (!summarySheet) {
      summarySheet = spreadsheet.insertSheet('Search Summary');
    }
    
    summarySheet.clear();
    
    // Add summary data
    const summaryData = [
      ['Search Summary'],
      [''],
      ['Location', '90210 (Beverly Hills)'],
      ['Distance', '25 miles'],
      ['Total Cars Found', allCars.length],
      ['Date', new Date().toLocaleString()],
      [''],
      ['Price Statistics'],
      ['Average Price', allCars.reduce((sum, car) => sum + (car.price || 0), 0) / allCars.length],
      ['Min Price', Math.min(...allCars.map(car => car.price || 0))],
      ['Max Price', Math.max(...allCars.map(car => car.price || 0))],
      [''],
      ['Year Statistics'],
      ['Average Year', allCars.reduce((sum, car) => sum + (car.year || 0), 0) / allCars.length],
      ['Oldest', Math.min(...allCars.map(car => car.year || 0))],
      ['Newest', Math.max(...allCars.map(car => car.year || 0))]
    ];
    
    summarySheet.getRange(1, 1, summaryData.length, 2).setValues(summaryData);
    summarySheet.autoResizeColumns(1, 2);
    
    Logger.log(`Comprehensive search completed: ${allCars.length} cars`);
    Logger.log(`Sheets created: 'Comprehensive Search' and 'Search Summary'`);
  } else {
    Logger.log('No cars found in comprehensive search');
  }
}

// Export functions for use in Google Apps Script
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    testApiConnection,
    scrapeCar,
    searchInventory,
    scrapeDealerInventory,
    populateSheetWithCars,
    getAllCarsFromMultiplePages
  };
}
