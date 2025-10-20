from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Product, Category, CartItem

api_bp = Blueprint('api', __name__)


@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'stock': p.stock,
        'description': p.description,
        'category_id': p.category_id
    } for p in products])

@api_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    """Get single product"""
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'stock': product.stock,
        'description': product.description,
        'category_id': product.category_id
    })

@api_bp.route('/cart', methods=['GET'])
@login_required
def get_cart():
    """Get user's cart"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': item.id,
        'product_id': item.product_id,
        'quantity': item.quantity,
        'product_name': item.product.name,
        'product_price': item.product.price
    } for item in cart_items])

@api_bp.route('/cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Check if item already in cart
    existing_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(new_item)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item added to cart'})


@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api_bp.errorhandler(400)
def api_bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
