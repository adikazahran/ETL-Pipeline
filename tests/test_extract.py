import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from utils.extract import (
    fetching_content,
    extract_raw_product_data,
    scrape_all_pages,
    get_current_timestamp
)
from bs4 import BeautifulSoup

SAMPLE_HTML = """
<div class="collection-card">
    <h3 class="product-title">Test Product</h3>
    <span class="price">$100.00</span>
    <p>Rating: ⭐ 4.5 / 5</p>
    <p>3 Colors</p>
    <p>Size: M</p>
    <p>Gender: Unisex</p>
</div>
"""

class TestExtract:
    def test_get_current_timestamp(self):
        timestamp = get_current_timestamp()
        assert isinstance(timestamp, str)
        # Verify it's a valid ISO format
        datetime.fromisoformat(timestamp)

    def test_fetching_content_success(self):
        with patch('requests.Session') as mock_session:
            mock_get = mock_session.return_value.get
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"<html>test</html>"
            
            result = fetching_content("http://test.com")
            assert result == b"<html>test</html>"

    def test_extract_raw_product_data_with_timestamp(self):
        soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')
        product_card = soup.find('div', class_='collection-card')
        result = extract_raw_product_data(product_card)
        
        assert 'extracted_at' in result
        datetime.fromisoformat(result['extracted_at'])  # Verify timestamp is valid

    @patch('utils.extract.fetching_content')
    def test_scrape_all_pages_timestamp(self, mock_fetch):
        mock_fetch.return_value = SAMPLE_HTML.encode()
        result = scrape_all_pages("http://test.com", max_pages=1)
        
        assert len(result) > 0
        for product in result:
            assert 'extracted_at' in product
            datetime.fromisoformat(product['extracted_at'])