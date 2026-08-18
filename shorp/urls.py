from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'shorp'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.product_list, name='product_list'),
    path('shop/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<str:key>/', views.update_cart, name='update_cart'),
    path('cart/remove/<str:key>/', views.remove_from_cart, name='remove_from_cart'),

    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/<int:order_id>/verify/', views.payment_verify, name='payment_verify'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]