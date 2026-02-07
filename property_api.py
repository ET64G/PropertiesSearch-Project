"""
Property API Client - Supports both mock and real API implementations.

This module provides a unified interface for fetching UK property listings.
Currently implements a mock API that returns realistic dummy data.
When ready to use a real API, implement the _fetch_from_real_api() method.
"""
import random
import time
from dataclasses import dataclass
from typing import List, Optional
from config import PropertyDataConfig


@dataclass
class PropertyListing:
    """Represents a single property listing."""
    address: str
    price: int
    bedrooms: int
    bathrooms: int
    property_type: str  # e.g., "house", "flat", "bungalow"
    description: str
    url: str
    location: str
    postcode: str
    area_sqft: Optional[int] = None


@dataclass
class SearchParameters:
    """Search criteria for property queries."""
    location: str
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None   
    property_type: Optional[str] = None  # "house", "flat", "bungalow", etc.
    radius_miles: Optional[int] = None


class PropertyAPIClient:
    """
    Client for fetching UK property listings.
    
    Supports mock mode (for development/testing) and real API mode.
    The interface remains the same regardless of which mode is used.
    """
    
    def __init__(self, config: PropertyDataConfig):
        self.config = config
        self.use_mock = config.use_mock
        
        if not self.use_mock and not config.api_key:
            raise ValueError("API key required when not using mock mode")
    
    def search_properties(self, params: SearchParameters) -> List[PropertyListing]:
        """
        Search for properties based on the given parameters.
        
        Args:
            params: SearchParameters object with search criteria
            
        Returns:
            List of PropertyListing objects matching the criteria
        """
        if self.use_mock:
            return self._fetch_from_mock_api(params)
        else:
            return self._fetch_from_real_api(params)
    
    def _fetch_from_mock_api(self, params: SearchParameters) -> List[PropertyListing]:
        """
        Generate realistic mock property data based on search parameters.
        
        This simulates API behavior:
        - Returns 3-8 properties per search
        - Filters by price range and bedrooms if specified
        - Includes realistic UK addresses and prices
        """
        # Simulate API delay (real APIs take time)
        time.sleep(0.5)
        
        # Generate a random number of properties (3-8)
        num_properties = random.randint(3, 8)
        
        # UK property data templates
        property_types = ["house", "flat", "bungalow", "terraced house", "semi-detached house"]
        if params.property_type:
            property_types = [pt for pt in property_types if params.property_type.lower() in pt.lower()]
            if not property_types:
                property_types = ["house"]  # fallback
        
        # UK street names and areas (realistic examples)
        streets = [
            "High Street", "Church Road", "Victoria Road", "Park Avenue",
            "Mill Lane", "Oak Close", "The Green", "Station Road",
            "London Road", "Main Street", "Elm Drive", "Chestnut Way"
        ]
        
        areas = {
            "london": ["SW1", "SW2", "NW1", "NW3", "E1", "E2", "W1", "W2"],
            "manchester": ["M1", "M2", "M3", "M4", "M14", "M20"],
            "birmingham": ["B1", "B2", "B3", "B15", "B16", "B17"],
            "leeds": ["LS1", "LS2", "LS6", "LS7", "LS8"],
            "bristol": ["BS1", "BS2", "BS3", "BS6", "BS7"],
        }
        
        # Get postcodes for location
        location_lower = params.location.lower()
        postcodes = areas.get(location_lower, ["SW1", "M1", "B1"])  # Default fallback
        
        properties = []
        
        for i in range(num_properties):
            # Generate property details
            property_type = random.choice(property_types)
            bedrooms = random.randint(1, 5)
            
            # Apply bedroom filter if specified
            if params.min_bedrooms and bedrooms < params.min_bedrooms:
                bedrooms = params.min_bedrooms
            if params.max_bedrooms and bedrooms > params.max_bedrooms:
                bedrooms = params.max_bedrooms
            
            # Generate price based on location and property type
            base_prices = {
                "london": {"house": 600000, "flat": 400000, "bungalow": 500000},
                "manchester": {"house": 250000, "flat": 150000, "bungalow": 200000},
                "birmingham": {"house": 200000, "flat": 120000, "bungalow": 180000},
            }
            
            location_key = location_lower if location_lower in base_prices else "birmingham"
            type_key = property_type if property_type in base_prices[location_key] else "house"
            base_price = base_prices[location_key][type_key]
            
            # Adjust price by bedrooms
            price = base_price + (bedrooms - 2) * 50000
            price = int(price * random.uniform(0.8, 1.3))  # Add some variation
            
            # Apply price filters
            if params.min_price and price < params.min_price:
                price = params.min_price + random.randint(10000, 50000)
            if params.max_price and price > params.max_price:
                price = params.max_price - random.randint(10000, 50000)
            
            # Ensure price is reasonable
            price = max(80000, min(price, 2000000))
            
            # Generate address
            street_num = random.randint(1, 200)
            street = random.choice(streets)
            postcode = random.choice(postcodes) + " " + str(random.randint(1, 9)) + random.choice("ABDEFGHJKLMNOPQRSTUVWXYZ") + random.choice("ABDEFGHJKLMNOPQRSTUVWXYZ")
            
            address = f"{street_num} {street}, {params.location.title()}"
            
            # Generate description
            descriptions = [
                f"Beautiful {property_type} in {params.location.title()}",
                f"Stunning {bedrooms}-bedroom {property_type}",
                f"Modern {property_type} with excellent transport links",
                f"Spacious {bedrooms}-bedroom {property_type} in sought-after area",
            ]
            description = random.choice(descriptions)
            
            # Generate URL (mock)
            property_id = random.randint(100000, 999999)
            url = f"https://example-property-site.co.uk/property/{property_id}"
            
            # Generate area
            area_sqft = random.randint(600, 2000) if bedrooms > 1 else random.randint(400, 800)
            
            # Generate bathrooms (usually 1-2 for smaller properties, more for larger)
            bathrooms = min(bedrooms, random.randint(1, 3))
            
            property_listing = PropertyListing(
                address=address,
                price=price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                property_type=property_type,
                description=description,
                url=url,
                location=params.location.title(),
                postcode=postcode,
                area_sqft=area_sqft,
            )
            
            properties.append(property_listing)
        
        # Sort by price (lowest first)
        properties.sort(key=lambda p: p.price)
        
        return properties
    
    def _fetch_from_real_api(self, params: SearchParameters) -> List[PropertyListing]:
        """
        Fetch properties from a real API.
        
        TODO: Implement this method when you have access to a real property API.
        Example structure:
        
        import requests
        
        url = "https://api.propertydata.co.uk/v1/properties/search"
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        payload = {
            "location": params.location,
            "min_price": params.min_price,
            "max_price": params.max_price,
            "min_bedrooms": params.min_bedrooms,
            "max_bedrooms": params.max_bedrooms,
            "property_type": params.property_type,
        }
        
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        data = response.json()
        
        # Parse API response into PropertyListing objects
        properties = []
        for item in data.get("results", []):
            properties.append(PropertyListing(
                address=item["address"],
                price=item["price"],
                # ... map other fields
            ))
        
        return properties
        """
        raise NotImplementedError(
            "Real API not implemented yet. "
            "Set USE_MOCK_API=true in .env to use mock data, "
            "or implement _fetch_from_real_api() method."
        )
