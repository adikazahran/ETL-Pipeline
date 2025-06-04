import pytest
from utils.transform import transform_product_data
from datetime import datetime

def test_transform_product_data_complete():
    raw_data = [
        {
            'title': 'Test Product',
            'price': '$100.00',
            'rating_text': 'Rating: ⭐ 4.5 / 5',
            'colors_text': '3 Colors',
            'size_text': 'Size: M',
            'gender_text': 'Gender: Unisex',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    result = transform_product_data(raw_data)
    assert len(result) == 1
    product = result[0]
    assert product['Title'] == 'Test Product'
    assert product['Price'] == 100.0
    assert product['Rating'] == 4.5
    assert product['Colors'] == 3
    assert product['Size'] == 'M'
    assert product['Gender'] == 'Unisex'

def test_transform_with_missing_data():
    raw_data = [
        {
            'title': 'Incomplete Product',
            'price': '$50.00'
        }
    ]
    
    result = transform_product_data(raw_data)
    assert len(result) == 0  

def test_transform_with_invalid_price():
    raw_data = [
        {
            'title': 'Bad Price',
            'price': 'invalid',
            'rating_text': 'Rating: ⭐ 4.0 / 5'
        }
    ]
    
    result = transform_product_data(raw_data)
    assert len(result) == 0  
