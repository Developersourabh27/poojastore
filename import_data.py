import os
import django
import csv

# Django ko is script ke sath connect karna
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poojastore.settings')
django.setup()

from store.models import Product

def import_products():
    print("⏳ 1 Lakh cosmetics load hona shuru ho gaye hain... kripya wait karein.")
    
    # CSV file open karna
    with open('products.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        products_to_add = []
        count = 0
        
        for row in reader:
            products_to_add.append(
                Product(
                    name=row['name'],
                    price=float(row['price']),
                    description=row['description']
                )
            )
            count += 1
            
            # Har 5000 products ke baad save karna taaki PC hang na ho
            if len(products_to_add) == 5000:
                Product.objects.bulk_create(products_to_add)
                print(f"✅ {count} products add ho gaye...")
                products_to_add = [] 

        # Bachen hue products save karna
        if products_to_add:
            Product.objects.bulk_create(products_to_add)
            print(f"✅ {count} products add ho gaye...")

    print("🎉 BADHAI HO! Saare Cosmetics successfully database mein add ho gaye hain!")

if __name__ == '__main__':
    import_products()