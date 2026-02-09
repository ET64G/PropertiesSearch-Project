from config import load_config
from property_api import PropertyAPIClient, SearchParameters
from google_sheets import GoogleSheetsReader


def main() -> None:
    config = load_config()
    print("Config loaded OK")
    print(f"Email from: {config.smtp.email_from}")
    print(f"Using mock API: {config.propertydata.use_mock}")
    
    # Test the property API with a sample search
    print("\n--- Testing Property API ---")
    api_client = PropertyAPIClient(config.propertydata)

    print("\n--- Reading Search Parameters from Google Sheets ---")
    try:
        sheets_reader = GoogleSheetsReader(config.sheets)
        search_params_list = sheets_reader.get_search_parameters()
        print(f"Found {len(search_params_list)} search parameter(s) in Google Sheets")
        
        # Search for properties using each set of parameters from Google Sheets
        for search_num, search_params in enumerate(search_params_list, 1):
            print(f"\n--- Search {search_num}: {search_params.location} ---")
            print(f"  Price Range: £{search_params.min_price or 'any':,} - £{search_params.max_price or 'any':,}")
            print(f"  Bedrooms: {search_params.min_bedrooms or 'any'} - {search_params.max_bedrooms or 'any'}")
            if search_params.property_type:
                print(f"  Property Type: {search_params.property_type}")
            
            print(f"\nSearching for properties in {search_params.location}...")
            properties = api_client.search_properties(search_params)
            
            print(f"\nFound {len(properties)} properties:")
            for i, prop in enumerate(properties, 1):
                print(f"\n{i}. {prop.address}")
                print(f"   Price: £{prop.price:,}")
                print(f"   Bedrooms: {prop.bedrooms} | Bathrooms: {prop.bathrooms}")
                print(f"   Type: {prop.property_type}")
                print(f"   {prop.description}")
    
    except Exception as e:
        print(f"Error reading from Google Sheets: {e}")
        print("Falling back to hardcoded search parameters...")
        
        # Fallback to hardcoded search if Google Sheets fails
        search_params = SearchParameters(
            location="London",
            min_price=300000,
            max_price=600000,
            min_bedrooms=2,
            max_bedrooms=4,
            property_type="house"
        )
        
        print(f"\nSearching for properties in {search_params.location}...")
        properties = api_client.search_properties(search_params)
        
        print(f"\nFound {len(properties)} properties:")
        for i, prop in enumerate(properties, 1):
            print(f"\n{i}. {prop.address}")
            print(f"   Price: £{prop.price:,}")
            print(f"   Bedrooms: {prop.bedrooms} | Bathrooms: {prop.bathrooms}")
            print(f"   Type: {prop.property_type}")
            print(f"   {prop.description}")

if __name__ == "__main__":
    main()


