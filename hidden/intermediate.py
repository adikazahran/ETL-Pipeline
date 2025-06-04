import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def fetching_content(url):
    """Mengambil konten HTML dari URL yang diberikan."""
    session = requests.Session()
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan ketika melakukan requests terhadap {url}: {e}")
        return None

def extract_product_data(product_card):
    """Mengambil data produk dari elemen product card."""
    try:
        # Extract title
        title_elem = product_card.find('h3', class_='product-title')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
        
        # Extract price
        price_elem = product_card.find('span', class_='price')
        price_text = price_elem.get_text(strip=True) if price_elem else "$0.00"
        price = float(price_text.replace('$', '').replace(',', ''))
        
        # Extract rating
        rating_elem = product_card.find('p', string=lambda x: x and 'Rating' in str(x))
        rating_text = rating_elem.get_text(strip=True) if rating_elem else "Rating: ⭐ 0.0 / 5"
        rating = rating_text.split('⭐')[-1].split('/')[0].strip()
        if 'Invalid' in rating:
            rating = '0.0'
        
        # Extract colors
        colors_elem = product_card.find('p', string=lambda x: x and 'Colors' in str(x))
        colors_text = colors_elem.get_text(strip=True) if colors_elem else "0 Colors"
        colors = colors_text.split('Colors')[0].strip()
        
        # Extract size
        size_elem = product_card.find('p', string=lambda x: x and 'Size:' in str(x))
        size_text = size_elem.get_text(strip=True) if size_elem else "Size: NA"
        size = size_text.split('Size:')[-1].strip()
        
        # Extract gender
        gender_elem = product_card.find('p', string=lambda x: x and 'Gender:' in str(x))
        gender_text = gender_elem.get_text(strip=True) if gender_elem else "Gender: Unisex"
        gender = gender_text.split('Gender:')[-1].strip()
        
        product = {
            "Title": title,
            "Price": float(price),
            "Rating": float(rating),
            "Colors": int(colors),
            "Size": size,
            "Gender": gender
        }
        
        return product
    
    except Exception as e:
        print(f"Error extracting product data: {e}")
        return None

def scrape_all_pages(base_url, delay=1):
    """Fungsi untuk mengambil semua data dari semua halaman yang tersedia."""
    data = []
    page_number = 1
    max_pages = 50  
    session = requests.Session()
    
    while page_number <= max_pages:
        url = f"{base_url}/page{page_number}" if page_number > 1 else base_url
        print(f"Scraping halaman {page_number}...")
        
        content = fetching_content(url)
        if not content:
            print(f"Gagal mengambil halaman {page_number}, melanjutkan ke halaman berikutnya...")
            page_number += 1
            continue
            
        soup = BeautifulSoup(content, "html.parser")
        product_cards = soup.find_all('div', class_='collection-card')
        
        if not product_cards:
            print(f"Tidak menemukan produk di halaman {page_number}, mungkin sudah mencapai halaman terakhir.")
            break
            
        for card in product_cards:
            product = extract_product_data(card)
            if product:
                data.append(product)
        
        # Cek apakah ada halaman berikutnya
        next_button = soup.find('li', class_='next')
        if not next_button or 'disabled' in next_button.get('class', []):
            break
            
        page_number += 1
        time.sleep(delay)  # Delay 
    
    return data

def main():
    """Fungsi utama untuk keseluruhan proses scraping hingga menyimpannya."""
    BASE_URL = 'https://fashion-studio.dicoding.dev'
    print("Memulai proses scraping semua halaman...")
    
    all_products_data = scrape_all_pages(BASE_URL)
    
    if not all_products_data:
        print("Tidak ada data yang berhasil di-scrape.")
        return
    
    print(f"Berhasil mengumpulkan {len(all_products_data)} produk.")
    
    # Create DataFrame
    df = pd.DataFrame(all_products_data)
    
    # Add index column
    df.reset_index(inplace=True)
    df['index'] += 1
    
    # Reorder columns
    df = df[['index', 'Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender']]
    
    # Save to CSV
    csv_filename = 'all_fashion_products.csv'
    df.to_csv(csv_filename, index=False)
    print(f"Data berhasil disimpan ke {csv_filename}")
    
    # Tampilkan 5 data pertama 
    print("\nContoh 5 data pertama:")
    print(df.head())

if __name__ == '__main__':
    main()