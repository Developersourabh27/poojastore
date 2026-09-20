from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    

    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),
    path('cart/payment-success/', views.cart_payment_success, name='cart_payment_success'),
    
   
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('process-payment/<int:product_id>/', views.process_payment, name='process_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('api/verify-payment/', views.verify_payment_api, name='verify_payment_api'),
    

    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    

    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'), 
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
]