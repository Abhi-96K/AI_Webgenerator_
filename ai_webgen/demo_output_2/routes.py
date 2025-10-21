from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Product, Category, CartItem
from forms import ProductForm, CategoryForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/products')
def products():
    """List all products"""
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('products.html', products=products, categories=categories)

@main_bp.route('/products/<int:id>')
def product_detail(id):
    """Product detail page"""
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)

@main_bp.route('/admin/products', methods=['GET', 'POST'])
@login_required
def manage_products():
    """Manage products (admin only)"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.products'))
    
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category_id=form.category_id.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('main.manage_products'))
    
    products = Product.query.all()
    return render_template('admin/products.html', form=form, products=products)

@main_bp.route('/cart')
@login_required
def view_cart():
    """View shopping cart"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

