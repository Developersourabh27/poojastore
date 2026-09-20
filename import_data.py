import os
import json
import django

# Django environment setup karein
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poojastore.settings')
django.setup()

from store.models import Product

def import_bulk_products():
    print("Importing products in bulk, please wait...")
    
    # Agar aapke paas JSON file hai jisme saare 1 lakh products hain
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products_data = json.load(f)
            
        batch = []
        for item in products_data:
            # Batch list mein products add karein
            batch.append(
                Product(
                    name=item.get('name'),
                    price=item.get('price'),
                    description=item.get('description', 'Best quality product'),
                    # Aap yahan default ya placeholder image set kar sakte hain
                    image=item.get('image', 'products/default.jpg') 
                )
            )
            
            # Har 1000 items ke baad ek sath database mein save karein (Fast speed ke liye)
            if len(batch) >= 1000:
                Product.objects.bulk_create(batch)
                batch = []
                print("1000 products imported...")
                
        # Baki bache hue products save karne ke liye
        if batch:
            Product.objects.bulk_create(batch)
            
        print("🎉 Sabhi 1 lakh products successfully import ho gaye hain!")
        
    except Exception as e:
        print(f"Error aagya: {e}")

if __name__ == '__main__':
    import_bulk_products()