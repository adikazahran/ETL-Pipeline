from utils.extract import scrape_all_pages
from utils.transform import transform_product_data
from utils.load import save_to_csv, display_sample, load_to_gsheet, load_to_postgres

def main():
    BASE_URL = 'https://fashion-studio.dicoding.dev'
    DATABASE_URL = 'postgresql+psycopg2://developer:supersecretpassword@localhost:5432/companydb'
    
    print("=== ETL Pipeline Started ===")
    
    # Extraction
    print("\nExtracting data...")
    raw_data = scrape_all_pages(BASE_URL, max_pages=50)
    print(f"Extracted {len(raw_data)} raw products")
    
    # Transformation
    print("\nTransforming data...")
    transformed_data = transform_product_data(raw_data)
    print(f"Transformed {len(transformed_data)} products")
    
    # Loading
    print("\nLoading data...")
    save_to_csv(transformed_data, 'hasil_scraping.csv')
    display_sample(transformed_data)

    # GoogleSheets
    print("\nUploading to Google Sheets...")
    load_to_gsheet(transformed_data)

    # Upload to PostgreSQL
    print("\nUploading to PostgreSQL...")
    load_to_postgres(transformed_data, DATABASE_URL)
    
    print("\n=== ETL Pipeline Completed ===")

if __name__ == '__main__':
    main()