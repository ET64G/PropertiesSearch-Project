import os
from typing import List, Optional
import gspread
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound
from google.oauth2.service_account import Credentials
from property_api import SearchParameters
from config import GoogleSheetsConfig

class GoogleSheetsReader:
    """Reads property search parameters from Google Sheets."""

    def __init__(self, config: GoogleSheetsConfig):
        """Initialise with configuration."""
        self.config = config
        self.client = None
        self._authenticate()

    # Step 3.3: Implement Authentication
    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API using service account."""
        credentials_path = self.config.credentials_json
        
        # Check if file exists
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Google Sheets credentials file not found: {credentials_path}"
                f"Please download your service account JSON key from Google Cloud console."
            )

        # Define what we need access to
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Load credentials from JSON file
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        self.client = gspread.authorize(creds)

    # Step 3.4 Implement Reading the Sheet
    def get_search_parameters(self) -> List[SearchParameters]:
        """ Read and parse search parameters from the sheet."""
        try:
            # open the spreadsheet
            spreadsheet = self.client.open_by_key(self.config.spreadsheet_id)
            worksheet = spreadsheet.worksheet(self.config.worksheet_name)
        except SpreadsheetNotFound:
            raise ValueError(
                f"Spreadsheet not found. Please check that the spreadsheet ID is correct: "
                f"{self.config.spreadsheet_id}\n"
                f"Make sure you've shared the spreadsheet with your service account email."
            )
        except WorksheetNotFound:
            raise ValueError(
                f"Worksheet '{self.config.worksheet_name}' not found. "
                f"Please check the worksheet name in your spreadsheet."
            )
        except Exception as e:
            raise ValueError(f"Error accessing Google Sheets: {e}")

        # Get all values
        all_values = worksheet.get_all_values()

        if not all_values:
            raise ValueError("Worksheet is empty. Please check your spreadsheet and worksheet name.")

        # First row is headers
        headers = [h.strip().lower() for h in all_values[0]] # list of header strings

        # Find which column is which
        location_idx = self._find_column_index(headers, ["location", "city", "area"])
        min_price_idx = self._find_column_index(headers, ["min price", "min_price", "minimum price"])
        max_price_idx = self._find_column_index(headers, ["max price", "max_price", "maximum price"])
        min_bedrooms_idx = self._find_column_index(headers, ["min bedrooms", "min_bedrooms"])
        max_bedrooms_idx = self._find_column_index(headers, ["max bedrooms", "max_bedrooms"])
        property_type_idx = self._find_column_index(headers, ["property type", "property_type", "type"])
        radius_idx = self._find_column_index(headers, ["radius", "radius_miles"])

        # Location is required
        if location_idx is None:
            raise ValueError("Required column 'Location' not found in the worksheet.")

        # Parse each data row
        search_params = []
        for row_num, row in enumerate(all_values[1:], start=2):  # Skip header row
            # Skip empty rows
            if not any(cell.strip() for cell in row):
                continue

            # get location (required)
            location = row[location_idx].strip() if location_idx < len(row) else ""
            if not location:
                print(f"Warning: Row {row_num} has no location, skipping...")
                continue       
       
            # Parse optional fields
            min_price = self._parse_int(row, min_price_idx)
            max_price = self._parse_int(row, max_price_idx)
            min_bedrooms = self._parse_int(row, min_bedrooms_idx)
            max_bedrooms = self._parse_int(row, max_bedrooms_idx)
            property_type = self._parse_string(row, property_type_idx)
            radius = self._parse_int(row, radius_idx)

            # Create search parameters object
            search_param = SearchParameters(
                location=location,
                min_price=min_price,
                max_price=max_price,
                min_bedrooms=min_bedrooms,
                max_bedrooms=max_bedrooms,
                property_type=property_type,
                radius_miles=radius,
            )

            search_params.append(search_param)

        if not search_params:
            raise ValueError("No valid search parameters found in the worksheet.")
        
        return search_params


    # Step 3.5: Add Helper Methods
    def _find_column_index(self, headers: List[str], possible_names: List[str]) -> Optional[int]:
        """Find column index by checking multiple possible header names."""
        for name in possible_names:
            if name.lower() in headers:
                return headers.index(name.lower())
        return None
    
    def _parse_int(self, row: List[str], index: Optional[int]) -> Optional[int]:
        """Parse an integer from a cell, handling empty values and formatting."""
        if index is None or index >= len(row):
            return None
    
        value = row[index].strip()
        if not value:
            return None
    
        try:
            # Remove currency symbols and commas
            cleaned = value.replace("£", "").replace("$", "").replace(",", "").strip()
            return int(cleaned)
        except ValueError:
            return None

    def _parse_string(self, row: List[str], index: Optional[int]) -> Optional[str]:
        """Parse a string from a cell."""
        if index is None or index >= len(row):
            return None
    
        value = row[index].strip()
        return value if value else None
    
