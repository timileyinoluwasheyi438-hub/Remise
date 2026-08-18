from decimal import Decimal

from .models import Product

CART_SESSION_KEY = 'Remise_cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, size='', quantity=1):
        key = f'{product.id}_{size}'
        if key in self.cart:
            self.cart[key]['quantity'] += quantity
        else:
            self.cart[key] = {
                'product_id': product.id,
                'size': size,
                'quantity': quantity,
                'price': str(product.price),
            }
        self.save()

    def update(self, key, quantity):
        if key in self.cart:
            if quantity > 0:
                self.cart[key]['quantity'] = quantity
            else:
                del self.cart[key]
            self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        products_map = {p.id: p for p in products}

        for key, item in self.cart.items():
            product = products_map.get(item['product_id'])
            if not product:
                continue
            line = item.copy()
            line['key'] = key
            line['product'] = product
            line['price'] = Decimal(item['price'])
            line['total_price'] = line['price'] * item['quantity']
            yield line

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())