from config import load_config
from property_api import PropertyAPIClient, SearchParameters
from google_sheets import GoogleSheetsReader
from email_service import EmailService

def load_app_config():
    """Load and return the application configuration."""
    config = load_config()
    print("Config loaded OK")
    print(f"Email from: {config.smtp.email_from}")
    print(f"Using mock API: {config.propertydata.use_mock}")
    return config    

def get_search_parameters_from_sheets(config) -> list[SearchParameters]:
    """Read search parameters from Google Sheets, with nice error handling."""
    print("\n--- Reading Search Parameters from Google Sheets ---")
    try:
        sheets_reader = GoogleSheetsReader(config.sheets)
        search_params_list = sheets_reader.get_search_parameters()
        print(f"Found {len(search_params_list)} search parameter(s) in Google Sheets")
        for params in search_params_list:
            print(f"  - {params.location}")
        return search_params_list
    except Exception as e:
        print(f"Error reading from Google Sheets: {e}")
        print("Falling back to a single hardcoded search (London)...")
        fallback = SearchParameters(
            location="London",
            min_price=300000,
            max_price=600000,
            min_bedrooms=2,
            max_bedrooms=4,
            property_type="house",
        )
        return [fallback]

def run_search_and_email(
    api_client: PropertyAPIClient,
    email_service: EmailService,
    search_params: SearchParameters,
) -> None:

    """Run a property search for given parameters and send an email report."""
    print(f"\n--- Search: {search_params.location} ---")
    print(f"  Min price: {search_params.min_price or 'any'}")
    print(f"  Max price: {search_params.max_price or 'any'}")
    print(f"  Bedrooms: {search_params.min_bedrooms or 'any'} - {search_params.max_bedrooms or 'any'}")
    if search_params.property_type:
        print(f"  Property Type: {search_params.property_type}")
    
    print(f"\nSearching for properties in {search_params.location}...")
    properties = api_client.search_properties(search_params)

    print(f"\nFound {len(properties)} properties.")
    for i, prop in enumerate(properties[:5], 1):  # show first 5
        print(f"\n{i}. {prop.address}")
        print(f"   Price: £{prop.price:,}")
        print(f"   Bedrooms: {prop.bedrooms} | Bathrooms: {prop.bathrooms}")
        print(f"   Type: {prop.property_type}")
        print(f"   {prop.description}")
    if len(properties) > 5:
        print(f"\n... and {len(properties) - 5} more")

    if properties:
        print("\nSending email report...")
        html_content = email_service.format_properties_email(properties, search_params.location)
        subject = f"Property Search Results: {search_params.location}"
        email_service.send_email(subject, html_content)
    else:
        print("No properties found. Skipping email.")

def main() -> None:
    config = load_app_config()        
    api_client = PropertyAPIClient(config.propertydata)
    email_service = EmailService(config.smtp)

    search_params_list = get_search_parameters_from_sheets(config)

    for params in search_params_list:
        run_search_and_email(api_client, email_service, params)
          

if __name__ == "__main__":
    main()
