from flask import Blueprint, jsonify, request, session
from database.order_operations import (
    create_order,
    get_order,
    get_user_orders,
    update_order_status
)
import logging

bp = Blueprint('orders', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/orders', methods=['POST'])
def create_new_order():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    data = request.json
    required_fields = [
        'cart_items', 'email', 'shipping_address', 
        'billing_address', 'payment_method', 
        'payment_fee', 'total_price'
    ]
    
    # Kontrola povinných polí
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Pole {field} je povinné'}), 400
            
    # Kontrola adresy
    for address_type in ['shipping_address', 'billing_address']:
        address = data.get(address_type, {})
        address_fields = ['street', 'city', 'postal_code', 'country']
        for field in address_fields:
            if not address.get(field):
                return jsonify({'error': f'{field} v {address_type} je povinný'}), 400

    result = create_order(
        user_id=user_id,
        cart_items=data['cart_items'],
        email=data['email'],
        shipping_address=data['shipping_address'],
        billing_address=data['billing_address'],
        payment_method=data['payment_method'],
        payment_fee=data['payment_fee'],
        total_price=data['total_price']
    )

    if result.get('error'):
        error_logger.error('Vytvoření objednávky pro uživatele ID %s selhalo', user_id)
        return jsonify({'error': result['error']}), 400

    info_logger.info('Nová objednávka %s vytvořena pro uživatele %s', 
                    result['order']['id'], user_id)
    return jsonify(result), 201

@bp.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    result = get_order(order_id, user_id)
    
    if result.get('error'):
        return jsonify({'error': result['error']}), 404
        
    return jsonify({'order': result}), 200

@bp.route('/api/orders', methods=['GET'])
def get_orders():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    result = get_user_orders(user_id)
    
    if result.get('error'):
        return jsonify({'error': result['error']}), 400
        
    return jsonify(result), 200

@bp.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_status(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401

    data = request.json
    if not data or 'status' not in data:
        return jsonify({'error': 'Nový status je povinný'}), 400

    result = update_order_status(order_id, data['status'], user_id)
    
    if result.get('error'):
        error_logger.error('Aktualizace statusu objednávky %s selhala', order_id)
        return jsonify({'error': result['error']}), 400

    info_logger.info('Status objednávky %s byl změněn na %s', order_id, data['status'])
    return jsonify(result), 200