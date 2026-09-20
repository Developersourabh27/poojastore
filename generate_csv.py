import csv
import random

# Cosmetics aur Skincare ke liye naye words
brands = ["Lakmé", "Maybelline", "L'Oréal", "Sugar Cosmetics", "MAC", "Nykaa", "Colorbar", "Mamaearth", "Plum", "Minimalist", "Biotique", "Lotus Herbals", "Revlon", "Faces Canada"]
adjectives = ["Matte", "Dewy", "Waterproof", "Hydrating", "Glowing", "Natural", "Vegan", "Long-Lasting", "Brightening", "Anti-Aging", "Smudge-proof", "HD"]
products = ["Liquid Lipstick", "Foundation", "Eyeliner", "Mascara", "Vitamin C Serum", "Moisturizer", "Face Primer", "Liquid Concealer", "Highlighter", "Lip Balm", "Sunscreen SPF 50", "Face Wash", "Makeup Fixer"]
sizes = ["15ml", "30ml", "50g", "100g", "8g", "10ml", "120ml", "Pack of 2"]

print("⏳ 1 Lakh COSMETICS products ki CSV file ban rahi hai... Kripya wait karein.")

with open('products.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['name', 'price', 'description'])
    
    for i in range(1, 100001):
        # Random cosmetics naam banana (e.g., "Matte Lakmé Liquid Lipstick 15ml")
        name = f"{random.choice(adjectives)} {random.choice(brands)} {random.choice(products)} {random.choice(sizes)}"
        
        # Cosmetics thode premium hote hain, toh price 99 se 2999 ke beech rakhte hain
        price = round(random.uniform(99.0, 2999.0), 2)
        
        # Cosmetics style description
        desc = f"Achieve a flawless look with our premium {name.lower()}. Dermatologically tested and safe for all skin types. (Batch ID: #{i})"
        
        writer.writerow([name, price, desc])

print("🎉 DONE! Aapki nayi 'products.csv' file tayar hai jisme 1,00,000 Cosmetics items hain!")