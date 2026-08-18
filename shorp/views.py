import uuid

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, SignUpForm
from .models import Category, Order, OrderItem, Product, Wishlist


def home(request):
    gender = request.GET.get('gender', 'women')
    categories = Category.objects.all()
    trending = Product.objects.filter(is_active=True, gender__in=[gender, 'unisex'])[:8]
    new_in = Product.objects.filter(is_active=True, is_new=True, gender__in=[gender, 'unisex']).first()

    context = {
        'categories': categories,
        'trending': trending,
        'new_in': new_in,
        'active_gender': gender,
    }
    return render(request, 'shorp/home.html', context)


def product_list(request, category_slug=None):
    gender = request.GET.get('gender', 'women')
    query = request.GET.get('q', '')

    products = Product.objects.filter(is_active=True, gender__in=[gender, 'unisex'])
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if query:
        products = products.filter(name__icontains=query)

    context = {
        'categories': Category.objects.all(),
        'category': category,
        'products': products,
        'active_gender': gender,
        'query': query,
    }
    return render(request, 'shorp/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'related': related,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'shorp/product_detail.html', context)


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    size = request.POST.get('size', '')
    quantity = int(request.POST.get('quantity', 1))

    if product.sizes.exists() and not size:
        messages.error(request, 'Please select a size first.')
        return redirect(product.get_absolute_url())

    cart = Cart(request)
    cart.add(product=product, size=size, quantity=quantity)
    messages.success(request, f'{product.name} added to your bag.')

    next_url = request.POST.get('next') or reverse('shorp:cart_detail')
    return redirect(next_url)


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shorp/cart.html', {'cart': cart})


@require_POST
def update_cart(request, key):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(key, quantity)
    return redirect('shorp:cart_detail')


@require_POST
def remove_from_cart(request, key):
    cart = Cart(request)
    cart.remove(key)
    return redirect('shorp:cart_detail')


@require_POST
def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to save items to your wishlist.')
        return redirect('shorp:login')

    product = get_object_or_404(Product, id=product_id)
    wish, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wish.delete()
        messages.info(request, 'Removed from wishlist.')
    else:
        messages.success(request, 'Added to wishlist.')

    next_url = request.POST.get('next') or product.get_absolute_url()
    return redirect(next_url)


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, 'Your bag is empty.')
        return redirect('shorp:product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total = cart.get_total()
            order.paystack_reference = uuid.uuid4().hex[:20]
            order.save()

            for line in cart:
                OrderItem.objects.create(
                    order=order,
                    product=line['product'],
                    product_name=line['product'].name,
                    size=line['size'],
                    price=line['price'],
                    quantity=line['quantity'],
                )

            request.session['pending_order_id'] = order.id
            return redirect('shorp:payment', order_id=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'full_name': request.user.get_full_name(), 'email': request.user.email}
        form = CheckoutForm(initial=initial)

    return render(request, 'shorp/checkout.html', {'form': form, 'cart': cart})


def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
        'amount_kobo': int(order.total * 100),
        'callback_url': request.build_absolute_uri(reverse('shorp:payment_verify', args=[order.id])),
    }
    return render(request, 'shorp/payment.html', context)


def payment_verify(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    reference = request.GET.get('reference', order.paystack_reference)

    verified = False
    secret_key = settings.PAYSTACK_SECRET_KEY
    if secret_key and 'xxxx' not in secret_key:
        url = f'https://api.paystack.co/transaction/verify/{reference}'
        headers = {'Authorization': f'Bearer {secret_key}'}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            verified = data.get('data', {}).get('status') == 'success'
        except requests.RequestException:
            verified = False
    else:
        verified = True  # no live keys yet -> auto-pass in dev so you can demo checkout

    if verified:
        order.status = 'paid'
        order.paystack_reference = reference
        order.save()
        Cart(request).clear()
        return redirect('shorp:order_success', order_id=order.id)

    messages.error(request, 'Payment could not be verified. Please try again.')
    return redirect('shorp:payment', order_id=order.id)


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shorp/order_success.html', {'order': order})


def about(request):
    return render(request, 'shorp/about.html')


def contact(request):
    if request.method == 'POST':
        messages.success(request, "Thanks for reaching out — we'll get back to you soon.")
        return redirect('shorp:contact')
    return render(request, 'shorp/contact.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Remise, {user.username}!')
            return redirect('shorp:home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shorp/my_orders.html', {'orders': orders})
