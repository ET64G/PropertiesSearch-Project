## UK Property Search Automation (v1)

A Python program that:

- Reads **search parameters** from a **Google Sheet**
- Fetches **mock UK property listings** via a property API client
- **Formats** the results into an HTML email
- **Sends** the email via SMTP

The code is structured so a real property API can replace the mock client later.

## 1. Project Structure

- `main.py` – Orchestrates the whole process
- `config.py` – Loads configuration from `.env`
- `google_sheets.py` – Reads search parameters from Google Sheets
- `property_api.py` – Mock property API client that returns realistic dummy data
- `email_service.py` – Formats and sends emails
- `requirements.txt` – Python dependencies

## 2. Setup

### 2.1. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # on Windows
```

### 2.2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configuration (`.env`)

Create a `.env` file in the project root (same folder as `main.py`) with:

```bash
# Use mock property API (no real API key required)
USE_MOCK_API=true
PROPERTYDATA_API_KEY=

# Email / SMTP settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_email_app_password
EMAIL_FROM=your_email@example.com
EMAIL_TO=recipient@example.com

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_JSON=google-credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_SHEETS_WORKSHEET_NAME=Sheet1
```

Notes:

- For Gmail, use an **App Password** for `SMTP_PASSWORD` (not your normal password).
- `USE_MOCK_API=true` means the program uses dummy data and does **not** call a real property API.

## 4. Google Sheets Setup

1. Create a new Google Sheet.
2. Set the **first row** (header) to:

   ```text
   Location | Min Price | Max Price | Min Bedrooms | Max Bedrooms | Property Type | Radius
   ```

3. Add one or more data rows, e.g.:

   ```text
   London     | 300000 | 600000 | 2 | 4 | house | 5
   Manchester | 150000 | 300000 | 1 | 3 | flat  | 10
   ```

4. In the sheet URL:

   `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`

   Copy `SPREADSHEET_ID_HERE` into `GOOGLE_SHEETS_SPREADSHEET_ID` in `.env`.

## 5. Google API Credentials

1. In Google Cloud Console:
   - Create a project.
   - Enable **Google Sheets API** and **Google Drive API**.
2. Create a **Service Account** and download the JSON key.
3. Save the file into the project folder, e.g. `google-credentials.json`.
4. Share your Google Sheet with the service account email (from the JSON file) with **Viewer** access.
5. Ensure `.env` points to the correct JSON file:

   ```bash
   GOOGLE_SHEETS_CREDENTIALS_JSON=google-credentials.json
   ```

## 6. Running the Program

With the virtual environment activated and `.env` configured:

```bash
python main.py
```

What happens:

1. Config is loaded from `.env`.
2. Search parameters are read from Google Sheets.
3. For each row:
   - The mock property API returns a list of matching properties.
   - Results are printed to the console.
   - An HTML email with the results is sent to `EMAIL_TO`.

## 7. Notes and Next Steps

- **Version 1** uses a mock API only; `_fetch_from_real_api` in `property_api.py` is a stub.
- To move to a real API later:
  - Set `USE_MOCK_API=false`
  - Provide a real `PROPERTYDATA_API_KEY`
  - Implement `_fetch_from_real_api` to call the real service.
- The script can later be scheduled (e.g. Windows Task Scheduler) to run daily at 06:00.

