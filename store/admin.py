from django.contrib import admin
from .models import Product, UserProfile, Order, CartItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'payment_method', 'payment_status')
    list_editable = ('payment_status',) 
    list_filter = ('payment_status', 'payment_method')
    search_fields = ('user__username', 'payment_status')

admin.site.register(Order, OrderAdmin)
admin.site.register(CartItem)

admin.site.register(Product)
admin.site.register(UserProfile) 