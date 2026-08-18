from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shorp.models import Category, Product, ProductSize, ProductImage

# Generic extra angles used to fill out each product's gallery (2 per product)
EXTRA_GALLERY = [
    'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=700&q=80',
    'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=700&q=80',
    'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=700&q=80',
    'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=700&q=80',
]

CATEGORIES = [
    ('Dresses', '👗'),
    ('Tops', '👚'),
    ('Shoes', '👠'),
    ('Beauty', '💄'),
    ('Accessories', '👜'),
]

PRODUCTS = [
    # name, category, gender, price, old_price, image, is_new, is_bestseller, description
    ('Knitted Sweater', 'Dresses', 'women', 49.00, None,
     'https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=600&q=80', True, False,
     'A cosy ribbed knit sweater cut for an easy, relaxed fit. Layer it over midi skirts or wear with denim.'),
    ('Oversized Blazer', 'Tops', 'women', 89.00, None,
     'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=600&q=80', False, True,
     'A sharp oversized blazer with structured shoulders — the one piece that pulls any outfit together.'),
    ('Slip Midi Dress', 'Dresses', 'women', 65.00, None,
     'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80', True, False,
     'A bias-cut satin slip dress that skims the body. Dress it up with heels or down with sneakers.'),
    ('Relaxed Shirt', 'Tops', 'women', 39.00, None,
     'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=600&q=80', False, False,
     'An easy relaxed-fit cotton shirt for everyday wear, from the office to the weekend.'),
    ('Oversized Knitted Dress', 'Dresses', 'women', 700.00, 950.00,
     'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=900&q=80', False, True,
     "Check out this comfy oversized knitted dress from Remise. It's made with care, "
     "has some cool functional details and a sleek look — perfect for anyone who loves style and comfort."),
    ('Pleated Midi Skirt', 'Dresses', 'women', 55.00, None,
     'https://images.unsplash.com/photo-1583496661160-fb5886a13d77?w=600&q=80', True, False,
     'A flowing pleated midi skirt with a fluid drape that moves with every step.'),
    ('Wide Leg Trousers', 'Tops', 'women', 58.00, None,
     'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=600&q=80', False, False,
     'Tailored wide-leg trousers with a high waist for a clean, elongated silhouette.'),
    ('Strappy Heeled Sandals', 'Shoes', 'women', 72.00, None,
     'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&q=80', False, True,
     'Strappy heeled sandals finished in soft leather — the go-to pair for evenings out.'),
    ('Classic White Sneakers', 'Shoes', 'men', 68.00, None,
     'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&q=80', True, False,
     'Clean, minimal leather sneakers built for everyday wear with any outfit.'),
    ('Denim Jacket', 'Tops', 'men', 74.00, None,
     'https://images.unsplash.com/photo-1543087903-1ac2ec7aa8c5?w=600&q=80', False, False,
     'A classic mid-wash denim jacket that layers over almost anything in your wardrobe.'),
    ('Crew Neck T-Shirt', 'Tops', 'men', 25.00, None,
     'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80', False, True,
     'A heavyweight cotton crew-neck tee with a boxy, relaxed cut.'),
    ('Leather Belt Bag', 'Accessories', 'unisex', 45.00, None,
     'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600&q=80', True, False,
     'A compact leather belt bag with adjustable strap — hands-free for every day.'),
]


class Command(BaseCommand):
    help = 'Seeds the Remise shorp with demo categories and products.'

    def handle(self, *args, **options):
        cat_map = {}
        for order, (name, icon) in enumerate(CATEGORIES):
            cat, _ = Category.objects.get_or_create(
                slug=slugify(name), defaults={'name': name, 'icon': icon, 'order': order}
            )
            cat_map[name] = cat

        created = 0
        for (name, cat_name, gender, price, old_price, image_url,
             is_new, is_bestseller, description) in PRODUCTS:
            slug = slugify(name)
            product, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults=dict(
                    category=cat_map[cat_name],
                    name=name,
                    gender=gender,
                    price=price,
                    old_price=old_price,
                    image_url=image_url,
                    is_new=is_new,
                    is_bestseller=is_bestseller,
                    description=description,
                    rating=4.8,
                    review_count=120,
                    stock=50,
                )
            )
            if was_created:
                created += 1
                for size in ['XS', 'S', 'M', 'L', 'XL']:
                    ProductSize.objects.create(product=product, size=size, stock=10)
                for i in range(2):
                    ProductImage.objects.create(
                        product=product,
                        image_url=EXTRA_GALLERY[(created + i) % len(EXTRA_GALLERY)],
                        order=i,
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete. {created} products created ({Category.objects.count()} categories total).'
        ))