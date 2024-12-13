from enum import Enum
from datetime import datetime
from . import db

class PaymentMethod(Enum):
    CASH_ON_DELIVERY = 'cash_on_delivery'  # Dobírka
    BANK_TRANSFER = 'bank_transfer'        # Bankovní převod
    CARD_ONLINE = 'card_online'            # Kartou online

class OrderStatus(Enum):
    PENDING = 'pending'           # Čeká na zpracování
    CONFIRMED = 'confirmed'       # Potvrzeno
    PAID = 'paid'                # Zaplaceno
    SHIPPED = 'shipped'          # Odesláno
    DELIVERED = 'delivered'      # Doručeno
    CANCELLED = 'cancelled'      # Zrušeno

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Kontaktní informace
    email = db.Column(db.String(120), nullable=False)

    # Doručovací adresa (povinná)
    shipping_street = db.Column(db.String(200), nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_postal_code = db.Column(db.String(10), nullable=False)
    shipping_country = db.Column(db.String(100), nullable=False)

    # Fakturační adresa (povinná)
    billing_street = db.Column(db.String(200), nullable=False)
    billing_city = db.Column(db.String(100), nullable=False)
    billing_postal_code = db.Column(db.String(10), nullable=False)
    billing_country = db.Column(db.String(100), nullable=False)

    # Platební informace
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    payment_fee = db.Column(db.Float, nullable=False, default=0.0)  # Přirážka za platbu
    total_price = db.Column(db.Float, nullable=False)  # Celková cena včetně přirážky

    # Status objednávky
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)

    # GDPR souhlas
    gdpr_consent = db.Column(db.Boolean, nullable=False)
    gdpr_consent_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Vztahy
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.id}>'

# Položky objednávky
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_isbn10 = db.Column(db.String(10), db.ForeignKey('book.ISBN10'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(db.Float, nullable=False)  # Cena v době objednávky

    # Vztahy
    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    book = db.relationship('Book', backref=db.backref('order_items', lazy=True))

    def __repr__(self):
        return f'<OrderItem {self.id} - Order {self.order_id}>'