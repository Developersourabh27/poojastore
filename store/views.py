from itertools import product
from django.db.models import Q
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, UserProfile, Order, CartItem
from django.http import JsonResponse
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import json

VALID_ROHTAK_PINCODES = ['124001', '124021', '124022', '124303', '124411', '124412', '124113']


def home(request):
    # .strip() se aage-peeche ke extra spaces hat jayenge
    category = request.GET.get('category', 'All').strip()
    sort_by = request.GET.get('sort', '')
    
    products = Product.objects.all()

    if category != 'All':
        # Exact naam ki jagah hum 'in' use karenge taaki thodi spelling/space change ho toh bhi chal jaye
        if 'Make' in category or 'make' in category.lower():
            products = products.filter(
                Q(name__icontains='makeup') | 
                Q(name__icontains='lipstick') | 
                Q(name__icontains='lip') |         # Added 'lip' for lip balms
                Q(name__icontains='mascara') | 
                Q(name__icontains='kajal') | 
                Q(name__icontains='primer') | 
                Q(name__icontains='highlighter') |
                Q(name__icontains='foundation') |
                Q(name__icontains='blush')
            )
        elif 'Skin' in category or 'skin' in category.lower():
            products = products.filter(
                Q(name__icontains='serum') | 
                Q(name__icontains='cream') | 
                Q(name__icontains='lotion') | 
                Q(name__icontains='face') | 
                Q(name__icontains='wash') |
                Q(name__icontains='cleanser')
            )
        elif 'Hair' in category or 'hair' in category.lower():
            products = products.filter(
                Q(name__icontains='hair') | 
                Q(name__icontains='shampoo') | 
                Q(name__icontains='oil') |
                Q(name__icontains='conditioner')
            )
        else:
            # Agar upar walo me se koi nahi hai, tab normal naam search karega
            products = products.filter(name__icontains=category)

    # 👇 LOW PRICE SORTING 👇
    if sort_by == 'low_price':
        products = products.order_by('price') # Saste se Mehnga

    products = products[:40]

    context = {
        'products': products,
        'selected_category': category
    }
    return render(request, 'store/home.html', context)
class CustomRegistrationForm(UserCreationForm):
    phone = forms.CharField(
        max_length=15, 
        required=True, 
        label="Mobile Number",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your 10-digit mobile number'})
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Check karein ki kya yeh phone number database me pehle se hai?
        if UserProfile.objects.filter(phone=phone).exists():
            raise ValidationError(" Yeh Mobile Number pehle se kisi aur account me registered hai.")
        return phone

def register(request):
    if request.method == 'POST':
        # Ab hum apna Naya Custom Form use karenge
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone = form.cleaned_data.get('phone')
            
            # UserProfile banayein aur phone number save karein
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()
            
            username = form.cleaned_data.get('username')
            messages.success(request, f"Welcome {username}! Aapka account successfully ban gaya hai. Kripya login karein.")
            return redirect('login') 
    else:
        form = CustomRegistrationForm()
        
    return render(request, 'store/register.html', {'form': form})

@login_required(login_url='login')
def custom_logout(request):
    logout(request)
    messages.info(request, "Aap successfully logout ho chuke hain. Phir milenge!")
    return redirect('home') 

from django.contrib.auth import authenticate, login

# 👇 NAYA LOGIN VIEW (Mobile Number se Login ke liye) 👇
def custom_login(request):
    if request.method == 'POST':
        phone_input = request.POST.get('phone')
        password_input = request.POST.get('password')
        
        # 1. Database me check karein ki kya is mobile number ka koi UserProfile hai?
        profile = UserProfile.objects.filter(phone=phone_input).first()
        
        if profile:
            # 2. Agar profile mil gayi, toh uske jode hue user ka username nikal lein
            username = profile.user.username
            
            # 3. Ab username aur password se authenticate karein
            user = authenticate(request, username=username, password=password_input)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}! 💖")
                return redirect('home')
            else:
                messages.error(request, "Password galat hai. Kripya dobara try karein.")
        else:
            # Agar mobile number database me nahi mila
            messages.error(request, "Yeh Mobile Number humare pas registered nahi hai. Kripya naya account banayein (Sign up).")
            
    # GET request par (ya error hone par) wapas login page dikhayein
    return render(request, 'store/login.html')
# ===============================
# 2. PRODUCT & CART LOGIC
# ===============================

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Related products (Jis product par hain usko chhod kar baaki 6 products dikhayenge)
    related_products = Product.objects.exclude(id=product_id).order_by('?')[:6]
    
    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'store/product_detail.html', context)

@login_required(login_url='login')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # 👇 Naya: Form se Size nikalna 👇
        size = request.POST.get('size', '') 
        action = request.POST.get('action')

        # Size ke sath item ko cart me check/create karna
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, 
            product=product,
            size=size  # Size add kar diya
        )
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        size_text = f" (Size: {size})" if size else ""
        messages.success(request, f"🛒 {product.name}{size_text} cart mein add ho gaya!")
        
        if action == 'buy':
            return redirect('cart_view')
        else:
            return redirect(request.META.get('HTTP_REFERER', 'home'))
            
    return redirect('home')

@login_required(login_url='login')
def update_cart(request, item_id, action):
    # try-except use karenge taaki agar item already delete ho gaya ho toh website crash na ho
    try:
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
    except CartItem.DoesNotExist:
        # Agar item nahi mila (e.g., double click ki wajah se delete ho chuka hai), toh wapas cart pe bhej do
        return redirect('cart_view')
    
    if action == 'increment':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete() # Agar quantity 1 se kam hui toh item delete kar do
    elif action == 'delete':
        cart_item.delete()
        
    return redirect('cart_view')

@login_required(login_url='login')
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_amount': round(total_amount, 2),
        'total_items': total_items
    }
    return render(request, 'store/cart.html', context)    

# ===============================
# 3. CART CHECKOUT & PAYMENT
# ===============================

@login_required(login_url='login')
def cart_checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items:
        return redirect('cart_view')
        
    grand_total = sum(item.total_price() for item in cart_items)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'COD':
            for item in cart_items:
                Order.objects.create(
                    user=request.user, 
                    product=item.product, 
                    payment_method='COD', 
                    payment_status='Confirmed'
                )
            cart_items.delete()
            messages.success(request, "Aapka order successfully place ho gaya hai! 🎉")
            return redirect('my_orders')
            
        elif payment_method == 'UPI':
            context = {
                'cart_items': cart_items,
                'grand_total': grand_total,
                'upi_id': "sourabhv1310@ybl" # Aapki Original UPI ID
            }
            return render(request, 'store/cart_upi_pay.html', context)

    context = {
        'cart_items': cart_items,
        'grand_total': grand_total
    }
    return render(request, 'store/cart_checkout.html', context)

@login_required(login_url='login')
def cart_payment_success(request):
    if request.method == 'POST':
        utr_number = request.POST.get('utr_number')
        cart_items = CartItem.objects.filter(user=request.user)
        
        if cart_items.exists():
            for item in cart_items:
                Order.objects.create(
                    user=request.user, 
                    product=item.product, 
                    payment_method='UPI', 
                    payment_status=f'UTR: {utr_number} (Pending Ver.)' 
                )
            cart_items.delete()
            messages.success(request, "Payment details received! Aapka order jaldi hi verify ho jayega. 🎉")
            return redirect('my_orders')
            
    return redirect('home')

# ===============================
# 4. SINGLE PRODUCT CHECKOUT (Fallback)
# ===============================

@login_required(login_url='login')
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        pincode_input = request.POST.get('pincode')
        
        if pincode_input not in VALID_ROHTAK_PINCODES:
            messages.error(request, f"Sorry! Hum abhi sirf Rohtak aur aaspas ke gaon mein delivery karte hain. {pincode_input} par delivery available nahi hai.")
            return redirect('checkout', product_id=product.id)
        
        profile.phone = request.POST.get('phone')
        profile.pincode = pincode_input
        profile.address = request.POST.get('address')
        profile.save()
        
        messages.success(request, "Aapka address verify aur save ho gaya hai!")
        return redirect('checkout', product_id=product.id)

    return render(request, 'store/checkout.html', {'product': product, 'profile': profile}) 

@login_required(login_url='login')
def process_payment(request, product_id):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        product = get_object_or_404(Product, id=product_id)
        
        if payment_method == 'COD':
            Order.objects.create(
                user=request.user, product=product, 
                payment_method='COD', payment_status='Confirmed'
            )
            return redirect('order_success')
            
        elif payment_method == 'UPI':
            upi_id = "sourabhv1310@ybl" 
            context = {
                'product': product,
                'upi_id': upi_id
            }
            return render(request, 'store/upi_pay.html', context)

    return redirect('checkout', product_id=product_id)

@login_required
def payment_success(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        utr_number = request.POST.get('utr_number') 
        product = get_object_or_404(Product, id=product_id)
        
        Order.objects.create(
            user=request.user, 
            product=product, 
            payment_method='UPI', 
            payment_status=f'UTR: {utr_number} (Pending Ver.)' 
        )
        return redirect('order_success')
    return redirect('home')

@login_required
def order_success(request):
    return render(request, 'store/success.html')
@csrf_exempt # Taaki Android app bina CSRF token ke aasaani se data bhej sake
def verify_payment_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            received_utr = data.get('utr', '').strip()
            received_amount = float(data.get('amount', 0))
            
            # Database mein dhoondhein ki yeh UTR kahan "Pending Ver." mein hai
            # Hum payment_status field me check karenge jisme UTR save hota hai
            orders = Order.objects.filter(payment_status__icontains=received_utr, payment_status__contains='Pending Ver.')
            
            if orders.exists():
                for order in orders:
                    # Optional: Amount match check kar sakte hain agar product price match karna ho
                    # order.payment_status = 'Confirmed (Auto-Verified)'
                    order.payment_status = 'Confirmed'
                    order.save()
                
                return JsonResponse({'status': 'success', 'message': 'Payment verified and order confirmed!'})
            else:
                return JsonResponse({'status': 'not_found', 'message': 'Matching UTR order not found.'}, status=404)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'invalid_method'}, status=405)

# ===============================
# 5. ORDER MANAGEMENT
# ===============================

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'store/my_orders.html', {'orders': orders})

@login_required(login_url='login')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_status != 'Cancelled':
        order.payment_status = 'Cancelled'
        order.save()
        messages.success(request, "Aapka order successfully cancel ho gaya hai. Koi baat nahi, hum asha karte hain ki aap jaldi wapas aayenge aur hume sewa ka mauka denge! 💙")
    return redirect('my_orders')

# ===============================
# 6. SEARCH & SUGGESTIONS
# ===============================

def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    if query:
        matched_products = Product.objects.filter(name__icontains=query)[:4]
        recommended_products = Product.objects.exclude(name__icontains=query).order_by('?')[:2]
        
        results = []
        for p in matched_products:
            results.append({
                'name': p.name, 
                'price': p.price, 
                'url': reverse('product_detail', args=[p.id]),
                'is_recommended': False
            })
            
        for p in recommended_products:
            results.append({
                'name': p.name, 
                'price': p.price, 
                'url': reverse('product_detail', args=[p.id]),
                'is_recommended': True
            })
            
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})    

def search(request):
    query = request.GET.get('q', '').strip().lower()
    products = Product.objects.all()

    if query:
        # 👇 UPDATED: Hinglish to English translation for Cosmetics 👇
        smart_keywords = {
            'creame': 'cream',
            'krim': 'cream',
            'lali': 'lipstick',
            'honth': 'lip',
            'ankh': 'eye',
            'kajal': 'eyeliner',
            'chehra': 'face',
            'bal': 'hair',
            'baal': 'hair',
            'tel': 'oil',
            'sabun': 'soap',
            'mehandi': 'henna',
            'gora': 'fairness',
            'chamak': 'glow'
        }

        search_term = query
        for hindi_word, eng_word in smart_keywords.items():
            if hindi_word in query:
                search_term = eng_word
                break

        products = products.filter(
            Q(name__icontains=search_term) | 
            Q(description__icontains=search_term) |
            Q(name__icontains=query) 
        )
    else:
        products = []
    
    return render(request, 'store/search_results.html', {'products': products, 'query': request.GET.get('q', '')})