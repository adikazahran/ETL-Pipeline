import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def get_current_timestamp():
    """Mengembalikan timestamp saat ini dalam format ISO 8601."""
    return datetime.now().isoformat()

def fetching_content(url):
    """Mengambil konten HTML dari URL yang diberikan."""
    session = requests.Session()
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.content
    # Error Handling
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan ketika melakukan requests terhadap {url}: {e}")
        return None

def extract_raw_product_data(product_card):
    """Mengambil data mentah produk dari elemen product card."""
    try:
        data = {
            "title": product_card.find('h3', class_='product-title').get_text(strip=True) if product_card.find('h3', class_='product-title') else None,
            "price": product_card.find('span', class_='price').get_text(strip=True) if product_card.find('span', class_='price') else None,
            "rating_text": product_card.find('p', string=lambda x: x and 'Rating' in str(x)).get_text(strip=True) if product_card.find('p', string=lambda x: x and 'Rating' in str(x)) else None,
            "colors_text": product_card.find('p', string=lambda x: x and 'Colors' in str(x)).get_text(strip=True) if product_card.find('p', string=lambda x: x and 'Colors' in str(x)) else None,
            "size_text": product_card.find('p', string=lambda x: x and 'Size:' in str(x)).get_text(strip=True) if product_card.find('p', string=lambda x: x and 'Size:' in str(x)) else None,
            "gender_text": product_card.find('p', string=lambda x: x and 'Gender:' in str(x)).get_text(strip=True) if product_card.find('p', string=lambda x: x and 'Gender:' in str(x)) else None,
            "extracted_at": get_current_timestamp()
        }
        return {k: v for k, v in data.items() if v is not None}
    # Error Handling       
    except Exception as e:
        print(f"Error extracting raw product data: {e}")
        return None

def scrape_all_pages(base_url, delay=1, max_pages=50):
    """Fungsi utama untuk mengambil semua data mentah dari website."""
    data = []
    page_number = 1
    
    while page_number <= max_pages:
        url = f"{base_url}/page{page_number}" if page_number > 1 else base_url
        print(f"Extracting page {page_number}...")
        
        content = fetching_content(url)
        if not content:
            # Error Handling
            print(f"Failed to fetch page {page_number}")
            page_number += 1
            continue
            
        soup = BeautifulSoup(content, "html.parser")
        product_cards = soup.find_all('div', class_='collection-card')
        
        for card in product_cards:
            product_data = extract_raw_product_data(card)
            if product_data and product_data.get('title'):
                product_data['timestamp'] = datetime.now().isoformat()
                data.append(product_data)
        
        page_number += 1
        time.sleep(delay)
    
    return data