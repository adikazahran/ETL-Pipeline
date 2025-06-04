# tests/test_load.py

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from utils.load import save_to_csv, display_sample, load_to_gsheet, load_to_postgres
import os # Import os untuk mengakses variabel lingkungan

# Fixture pytest untuk mem-mock variabel lingkungan selama pengujian
# `autouse=True` berarti fixture ini akan dijalankan untuk setiap tes secara otomatis
@pytest.fixture(autouse=True)
def mock_env_vars():
    # Menggunakan patch.dict untuk sementara mengatur variabel lingkungan
    with patch.dict(os.environ, {
        'SERVICE_ACCOUNT_FILE': 'mock_repogsheet.json', # Nilai mock
        'SPREADSHEET_ID': 'mock_spreadsheet_id',       # Nilai mock
        'RANGE_NAME': 'mock_range_name',               # Nilai mock
        'POSTGRES_DB_URL': 'postgresql://mock_user:mock_pass@mock_host/mock_db' # Nilai mock
    }):
        yield # Kode tes akan dijalankan di sini

SAMPLE_DATA = [
    {'Title': 'Product 1', 'Price': 100.0, 'Rating': 4.5},
    {'Title': 'Product 2', 'Price': 200.0, 'Rating': 3.5}
]

def test_save_to_csv_success(tmp_path):
    file_path = tmp_path / "test.csv"
    result = save_to_csv(SAMPLE_DATA, file_path)
    assert result is True
    assert file_path.exists()

    df = pd.read_csv(file_path)
    assert len(df) == 2
    assert "Title" in df.columns

@patch('pandas.DataFrame.to_csv')
def test_save_to_csv_failure(mock_to_csv):
    mock_to_csv.side_effect = Exception("Write error")
    result = save_to_csv(SAMPLE_DATA, "test.csv")
    assert result is False

def test_display_sample(capsys):
    display_sample(SAMPLE_DATA)
    captured = capsys.readouterr()
    assert "Product 1" in captured.out
    assert "Product 2" in captured.out
    assert "Sample of" in captured.out

def test_display_sample_empty(capsys):
    display_sample([])
    captured = capsys.readouterr()
    assert "No data to display" in captured.out

@patch('utils.load.Credentials.from_service_account_file')
@patch('utils.load.build')
def test_load_to_gsheet(mock_build, mock_creds):
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.spreadsheets.return_value.values.return_value.update.return_value.execute.return_value = {
        'updatedCells': 6
    }

    result = load_to_gsheet(SAMPLE_DATA)
    assert result is True
    # Verifikasi bahwa file akun layanan yang benar dicoba dimuat
    mock_creds.assert_called_with('mock_repogsheet.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])


@patch('sqlalchemy.create_engine')
@patch('pandas.DataFrame.to_sql')
def test_load_to_postgres(mock_to_sql, mock_engine):
    mock_engine.return_value = MagicMock()
    # Tes tanpa secara eksplisit meneruskan db_url, seharusnya menggunakan variabel env yang di-mock
    result = load_to_postgres(SAMPLE_DATA)
    assert result is True
    mock_engine.assert_called_with(os.getenv('POSTGRES_DB_URL'))

def test_load_to_postgres_db_url_override(mock_env_vars):
    # Tes bahwa db_url yang diberikan secara eksplisit akan mengesampingkan variabel lingkungan
    with patch('sqlalchemy.create_engine') as mock_create_engine, \
         patch('pandas.DataFrame.to_sql') as mock_to_sql:
        custom_db_url = "postgresql://custom:pass@custom_host/custom_db"
        result = load_to_postgres(SAMPLE_DATA, db_url=custom_db_url)
        assert result is True
        mock_create_engine.assert_called_with(custom_db_url)

def test_load_to_postgres_no_db_url_and_no_env_var():
    # Tes kasus di mana tidak ada db_url yang diberikan dan tidak ada di variabel lingkungan
    # Simpan nilai asli POSTGRES_DB_URL jika ada, lalu hapus sementara
    original_db_url = os.environ.pop('POSTGRES_DB_URL', None)
    try:
        with pytest.raises(ValueError, match="PostgreSQL database URL not provided and not found in environment variables."):
            load_to_postgres(SAMPLE_DATA)
    finally:
        # Kembalikan nilai asli setelah tes selesai
        if original_db_url is not None:
            os.environ['POSTGRES_DB_URL'] = original_db_url