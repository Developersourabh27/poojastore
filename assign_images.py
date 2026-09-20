import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poojastore.settings')
django.setup()

from store.models import Product

def assign_smart_images():
    products = Product.objects.all()
    count = 0
    
    for product in products:
        name_lower = product.name.lower()
        
        # Category ke hisaab se Unsplash ki professional image URLs
        if 'shampoo' in name_lower or 'hair' in name_lower:
            img_url = "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=500"
        elif 'oil' in name_lower:
            img_url = "https://images.unsplash.com/photo-1608248597359-994b61d5626e?w=500"
        elif 'cream' in name_lower or 'moisturizer' in name_lower or 'face wash' in name_lower:
            img_url = "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500"
        elif 'lipstick' in name_lower or 'makeup' in name_lower or 'foundation' in name_lower:
            img_url = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500"
        elif 'men' in name_lower or 'brief' in name_lower or 'trunk' in name_lower or 'vest' in name_lower:
            img_url = "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500"
        elif 'women' in name_lower or 'briefs' in name_lower or 'knickers' in name_lower:
            img_url = "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500"
        else:
            img_url = "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=500"
            
        # Agar aapne model me CharField banaya hai image URL ke liye:
        product.image = img_url  # ya product.image_url agar field wahi hai
        product.save()
        count += 1

    print(f"Successfully assigned smart images to {count} products!")

if __name__ == '__main__':
    assign_smart_images()