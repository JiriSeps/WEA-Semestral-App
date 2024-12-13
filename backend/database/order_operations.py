from datetime import datetime
from . import db
from .order import Order, OrderItem, PaymentMethod, OrderStatus
from .book import Book
from .user import User

def calculate_payment_fee(payment_method, subtotal):
    """Vypočítá přirážku za platební metodu"""
    if payment_method == PaymentMethod.CASH_ON_DELIVERY:
        return 50.0
    elif payment_method == PaymentMethod.CARD_ONLINE:
        return round(subtotal * 0.01, 2)  # 1% z ceny
    return 0.0  # Pro bankovní převod

def create_order(user_id, cart_items, email, shipping_address, billing_address, payment_method, payment_fee, total_price):
    """
    Creates a new order with GDPR consent from order form
    """
    try:
        # Ověření existence uživatele
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Uživatel neexistuje'}

        # Odstranit GDPR kontrolu z user profilu - používáme souhlas z formuláře

        # Vytvoření objednávky
        new_order = Order(
            user_id=user_id,
            email=email,
            shipping_street=shipping_address['street'],
            shipping_city=shipping_address['city'],
            shipping_postal_code=shipping_address['postal_code'],
            shipping_country=shipping_address['country'],
            billing_street=billing_address['street'],
            billing_city=billing_address['city'],
            billing_postal_code=billing_address['postal_code'],
            billing_country=billing_address['country'],
            payment_method=PaymentMethod[payment_method.upper()],
            payment_fee=payment_fee,
            total_price=total_price,
            gdpr_consent=True,  # Vždy True, protože formulář to vyžaduje
            gdpr_consent_date=datetime.utcnow(),
            status=OrderStatus.PENDING
        )

        # Přidání položek objednávky
        for item in cart_items:
            book = Book.query.filter(
                (Book.ISBN10 == item['isbn']) | (Book.ISBN13 == item['isbn'])
            ).first()

            if not book or not book.is_visible:
                db.session.rollback()
                return {'error': f'Kniha {item["isbn"]} není dostupná'}

            order_item = OrderItem(
                book_isbn10=book.ISBN10,
                quantity=item['quantity'],
                price_per_item=item['price']
            )
            new_order.items.append(order_item)

        # Uložení do databáze
        db.session.add(new_order)
        db.session.commit()

        return {
            'message': 'Objednávka byla úspěšně vytvořena',
            'order': format_order_data(new_order)
        }

    except Exception as e:
        db.session.rollback()
        return {'error': f'Chyba při vytváření objednávky: {str(e)}'}

def format_order_data(order):
    """Helper funkce pro formátování dat objednávky"""
    return {
        'id': order.id,
        'created_at': order.created_at.isoformat(),
        'email': order.email,
        'shipping_address': {
            'street': order.shipping_street,
            'city': order.shipping_city,
            'postal_code': order.shipping_postal_code,
            'country': order.shipping_country
        },
        'billing_address': {
            'street': order.billing_street,
            'city': order.billing_city,
            'postal_code': order.billing_postal_code,
            'country': order.billing_country
        },
        'payment_method': order.payment_method.value,
        'payment_fee': order.payment_fee,
        'total_price': order.total_price,
        'status': order.status.value,
        'items': [{
            'book_isbn10': item.book_isbn10,
            'title': item.book.Title,
            'quantity': item.quantity,
            'price_per_item': item.price_per_item
        } for item in order.items]
    }

def get_order(order_id, user_id=None):
    """
    Získá detail objednávky. Pokud je zadáno user_id, kontroluje i vlastnictví.
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return {'error': 'Objednávka nenalezena'}

        if user_id and order.user_id != user_id:
            return {'error': 'Neoprávněný přístup k objednávce'}

        return format_order_data(order)
    except Exception as e:
        return {'error': f'Chyba při získávání objednávky: {str(e)}'}

def get_user_orders(user_id):
    """
    Získá seznam všech objednávek uživatele
    """
    try:
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        return {'orders': [format_order_data(order) for order in orders]}
    except Exception as e:
        return {'error': f'Chyba při získávání objednávek: {str(e)}'}

def update_order_status(order_id, new_status, user_id=None):
    """
    Aktualizuje status objednávky
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return {'error': 'Objednávka nenalezena'}

        if user_id and order.user_id != user_id:
            return {'error': 'Neoprávněný přístup k objednávce'}

        if new_status not in OrderStatus.__members__:
            return {'error': 'Neplatný status objednávky'}

        order.status = OrderStatus[new_status]
        db.session.commit()

        return {
            'message': 'Status objednávky byl úspěšně aktualizován',
            'order': format_order_data(order)
        }
    except Exception as e:
        db.session.rollback()
        return {'error': f'Chyba při aktualizaci statusu objednávky: {str(e)}'}
