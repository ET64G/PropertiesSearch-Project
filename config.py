import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    email_from: str
    email_to: str


@dataclass
class PropertyDataConfig:
    api_key: str
    use_mock: bool = False  # Set to True to use mock data instead of real API


@dataclass
class GoogleSheetsConfig:
    credentials_json: str
    spreadsheet_id: str
    worksheet_name: str


@dataclass
class AppConfig:
    smtp: SMTPConfig
    propertydata: PropertyDataConfig
    sheets: GoogleSheetsConfig


def _get_env(name: str, *, required: bool = True, default: str | None = None) -> str:
    """Helper to read environment variables with a nice error if missing."""
    value = os.getenv(name, default)
    if required and (value is None or value.strip() == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def load_config() -> AppConfig:
    """Load and validate all configuration needed by the app."""
    smtp = SMTPConfig(
        host=_get_env("SMTP_HOST"),
        port=int(_get_env("SMTP_PORT")),
        username=_get_env("SMTP_USERNAME"),
        password=_get_env("SMTP_PASSWORD"),
        email_from=_get_env("EMAIL_FROM"),
        email_to=_get_env("EMAIL_TO"),
    )

    # API key is optional if using mock data
    use_mock = _get_env("USE_MOCK_API", required=False, default="true").lower() == "true"
    propertydata = PropertyDataConfig(
        api_key=_get_env("PROPERTYDATA_API_KEY", required=not use_mock, default=""),
        use_mock=use_mock,
    )

    sheets = GoogleSheetsConfig(
        credentials_json=_get_env("GOOGLE_SHEETS_CREDENTIALS_JSON"),
        spreadsheet_id=_get_env("GOOGLE_SHEETS_SPREADSHEET_ID"),
        worksheet_name=_get_env("GOOGLE_SHEETS_WORKSHEET_NAME"),
    )

    return AppConfig(
        smtp=smtp,
        propertydata=propertydata,
        sheets=sheets,
    )    


