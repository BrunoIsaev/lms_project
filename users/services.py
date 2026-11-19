import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def to_ascii(name):
    """Транслитерирует кириллицу в латиницу для Stripe."""
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    result = []
    for char in name.lower():
        result.append(translit.get(char, char))
    return ''.join(result)


def create_stripe_product(name, description=''):
    """Создаёт продукт в Stripe."""
    safe_name = to_ascii(name)[:40]
    return stripe.Product.create(name=safe_name, description=to_ascii(description)[:100])


def create_stripe_price(product_id, amount):
    """Создаёт цену в Stripe. amount передаётся в копейках."""
    return stripe.Price.create(
        product=product_id,
        unit_amount=int(float(amount) * 100),
        currency='rub',
    )


def create_stripe_session(price_id, success_url, cancel_url):
    """Создаёт checkout-сессию и возвращает ссылку на оплату."""
    return stripe.checkout.Session.create(
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )


def get_stripe_session(session_id):
    """Получает данные сессии по id (для проверки статуса)."""
    return stripe.checkout.Session.retrieve(session_id)
