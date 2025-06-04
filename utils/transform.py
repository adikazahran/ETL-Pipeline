import pandas as pd

def transform_product_data(raw_data):
    transformed_data = []

    for item in raw_data:
        try:
            # Transform price
            try:
                price = float(item.get('price', '$0').replace('$', '').replace(',', ''))
            except:
                continue 
            
            # Transform rating - handle 'Not Rated' case
            rating_text = item.get('rating_text', 'Rating: ⭐ 0.0 / 5')
            if 'Not Rated' in rating_text:
                rating = 0.0
            else:
                rating = rating_text.split('⭐')[-1].split('/')[0].strip()
                if 'Invalid' in rating:
                    rating = '0.0'
            rating = float(rating)

            # Filter produk dengan price 0 atau rating 0
            if price == 0 or rating == 0:
                continue
            
            # Transform colors
            colors_text = item.get('colors_text', '0 Colors')
            colors = colors_text.split('Colors')[0].strip()
            
            # Transform size
            size_text = item.get('size_text', 'Size: NA')
            size = size_text.split('Size:')[-1].strip()
            
            # Transform gender
            gender_text = item.get('gender_text', 'Gender: Unisex')
            gender = gender_text.split('Gender:')[-1].strip()
            
            transformed_data.append({
                "Title": item.get('title', 'Unknown Product'),
                "Price": price,
                "Rating": rating,
                "Colors": int(colors),
                "Size": size,
                "Gender": gender,
                "Timestamp": item.get('timestamp')
            })
        except Exception as e:
            print(f"Error transforming product {item.get('title')}: {e}")
            continue

    if not transformed_data:
        return []

    df = pd.DataFrame(transformed_data, columns=["Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"])
    df = df.dropna(subset=["Title", "Price", "Rating"])
    df = df.drop_duplicates(subset=["Title", "Price", "Size"])

    return df.to_dict(orient="records")
