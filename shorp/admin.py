from django.contrib import admin

from .models import Category, Product, ProductImage, ProductSize, Order, OrderItem, Wishlist


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 4


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'gender', 'price', 'old_price', 'is_new', 'is_bestseller', 'stock')
    list_filter = ('category', 'gender', 'is_new', 'is_bestseller')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSizeInline, ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'size', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'paystack_reference')
    inlines = [OrderItemInline]


admin.site.register(Wishlist)
admin.site.site_header = 'Remise Administration'