import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poojastore.settings')
django.setup()

from store.models import Product

def assign_smart_images_chunked():
    print("🚀 Processing products in chunks (no freezing)...")
    
    chunk_size = 5000
    total_count = Product.objects.count()
    print(f"Total products in database: {total_count}")
    
    processed = 0
    
    while processed < total_count:
        # Ek baar mein sirf 5000 products uthayega
        products = Product.objects.all()[processed:processed + chunk_size]
        updated_products = []
        
        for product in products:
            name_lower = product.name.lower()
            
            if 'shampoo' in name_lower or 'hair' in name_lower:
                product.image = "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=500"
            elif 'oil' in name_lower:
                product.image = "https://images.unsplash.com/photo-1608248597359-994b61d5626e?w=500"
            elif 'cream' in name_lower or 'moisturizer' in name_lower or 'face wash' in name_lower:
                product.image = "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500"
            elif 'lipstick' in name_lower or 'makeup' in name_lower or 'foundation' in name_lower:
                product.image = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500"
            elif 'men' in name_lower or 'brief' in name_lower or 'trunk' in name_lower or 'vest' in name_lower:
                product.image = "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500"
            elif 'women' in name_lower or 'briefs' in name_lower or 'knickers' in name_lower:
                product.image = "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500"
            else:
                product.image = "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=500"
                
            updated_products.append(product)
            
        if updated_products:
            # Batch mein database update karein
            Product.objects.bulk_update(updated_products, ['image'])
            processed += len(updated_products)
            print(f"✅ Processed {processed}/{total_count} products...")
            
    print("🎉 Sabhi 1 lakh products par successfully images assign ho gayi hain!")

if __name__ == '__main__':
    assign_smart_images_chunked()