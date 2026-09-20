import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poojastore.settings')
django.setup()

from store.models import Product

# Product model ke saare fields ki list print karein
print("--- PRODUCT MODEL FIELDS ---")
for field in Product._meta.get_fields():
    print(field.name)