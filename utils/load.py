# utils/load.py

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy import create_engine
from dotenv import load_dotenv 
import os 

# --- Load environment variables from .env file ---
# Pastikan ini dipanggil di awal skrip atau modul yang membutuhkan variabel ini
load_dotenv()

# ===== Fungsi menyimpan ke CSV =====
def save_to_csv(data, filename):
    """Menyimpan data ke file CSV."""
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data successfully saved to {filename}")
        return True
    # Error Handling
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False

# ===== Fungsi menampilkan sample data =====
def display_sample(data, num_samples=5):
    """Menampilkan sample data tanpa kolom No."""
    if not data:
        print("No data to display")
        return
    df = pd.DataFrame(data)
    print(f"\nSample of {num_samples} records:")
    print(df.head(num_samples))

# ===== Fungsi menyimpan ke Google Sheets =====
# Ambil nilai dari variabel lingkungan yang dimuat dari .env
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = os.getenv('RANGE_NAME')

def load_to_gsheet(data):
    """Mengirim data ke Google Sheets."""
    try:
        # Periksa apakah variabel lingkungan berhasil dimuat
        if not SERVICE_ACCOUNT_FILE or not SPREADSHEET_ID or not RANGE_NAME:
            raise ValueError("Google Sheets credentials (SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, or RANGE_NAME) not found in environment variables.")

        df = pd.DataFrame(data)
        values = df.values.tolist()

        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        body = {'values': values}
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"{result.get('updatedCells')} cells updated in Google Sheets.")
        return True
    # Error Handling
    except Exception as e:
        print(f"Error uploading to Google Sheets: {e}")
        return False

# ===== Fungsi menyimpan ke PostgreSQL =====
# db_url sekarang opsional, akan diambil dari .env jika tidak disediakan
def load_to_postgres(data, db_url=None, table_name='products'):
    """Menyimpan data ke PostgreSQL database."""
    # Jika db_url tidak diberikan secara eksplisit, coba ambil dari variabel lingkungan
    if db_url is None:
        db_url = os.getenv('POSTGRES_DB_URL')
        if db_url is None:
            raise ValueError("PostgreSQL database URL not provided and not found in environment variables.")

    try:
        df = pd.DataFrame(data)
        engine = create_engine(db_url)
        df.to_sql(table_name, engine, index=False, if_exists='replace')
        print(f"Data successfully saved to PostgreSQL table '{table_name}'")
        return True
    # Error Handling
    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")
        return False