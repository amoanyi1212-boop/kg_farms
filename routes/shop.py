from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from database import db
from models import Poultry, Livestock, EggInventory, ShopOrder
from utils.helpers import generate_receipt_number

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')


@shop_bp.route('/')
def home():
    poultry = Poultry.query.filter_by(status='Available').order_by(Poultry.bird_type).all()
    livestock = Livestock.query.filter_by(status='Available').order_by(Livestock.animal_type).all()
    eggs = EggInventory.query.filter_by(status='Available').filter(
        EggInventory.crates_in_stock > 0
    ).order_by(EggInventory.egg_type).all()
    return render_template('shop/home.html', poultry=poultry, livestock=livestock, eggs=eggs)


@shop_bp.route('/poultry')
def shop_poultry():
    birds = Poultry.query.filter_by(status='Available').order_by(Poultry.bird_type).all()
    return render_template('shop/poultry.html', birds=birds)


@shop_bp.route('/livestock')
def shop_livestock():
    animals = Livestock.query.filter_by(status='Available').order_by(Livestock.animal_type).all()
    return render_template('shop/livestock.html', animals=animals)


@shop_bp.route('/eggs')
def shop_eggs():
    eggs = EggInventory.query.filter_by(status='Available').filter(
        EggInventory.crates_in_stock > 0
    ).order_by(EggInventory.egg_type).all()
    return render_template('shop/eggs.html', eggs=eggs)


@shop_bp.route('/order', methods=['GET', 'POST'])
def place_order():
    if request.method == 'POST':
        try:
            preferred = request.form.get('preferred_date')
            order = ShopOrder(
                customer_name=request.form.get('customer_name', '').strip(),
                customer_phone=request.form.get('customer_phone', '').strip(),
                customer_email=request.form.get('customer_email', '').strip(),
                customer_location=request.form.get('customer_location', '').strip(),
                item_type=request.form.get('item_type'),
                item_description=request.form.get('item_description'),
                quantity=int(request.form.get('quantity', 1)),
                preferred_date=datetime.strptime(preferred, '%Y-%m-%d').date() if preferred else None,
                notes=request.form.get('notes'),
                order_number=generate_receipt_number(),
                status='Pending'
            )
            db.session.add(order)
            db.session.commit()
            flash(f'Order placed! Your order number is {order.order_number}', 'success')
            return redirect(url_for('shop.order_success', order_id=order.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    poultry = Poultry.query.filter_by(status='Available').all()
    livestock = Livestock.query.filter_by(status='Available').all()
    eggs = EggInventory.query.filter_by(status='Available').filter(
        EggInventory.crates_in_stock > 0
    ).all()
    return render_template('shop/order.html', poultry=poultry, livestock=livestock, eggs=eggs)


@shop_bp.route('/order/success/<int:order_id>')
def order_success(order_id):
    order = ShopOrder.query.get_or_404(order_id)
    return render_template('shop/order_success.html', order=order)


@shop_bp.route('/track', methods=['GET', 'POST'])
def track_order():
    order = None
    order_number = request.form.get('order_number') or request.args.get('order_number')
    if order_number:
        order = ShopOrder.query.filter_by(order_number=order_number.strip()).first()
        if not order and request.method == 'POST':
            flash('Order not found. Please check your order number.', 'warning')
    return render_template('shop/track.html', order=order)


@shop_bp.route('/about')
def about():
    return render_template('shop/about.html')


@shop_bp.route('/contact')
def contact():
    return render_template('shop/contact.html')


# ==================== ADMIN ORDER MANAGEMENT ====================
@shop_bp.route('/admin/orders')
@login_required
def manage_orders():
    filter_status = request.args.get('status', '')
    query = ShopOrder.query
    if filter_status:
        query = query.filter_by(status=filter_status)
    orders = query.order_by(ShopOrder.created_at.desc()).all()

    pending_count = ShopOrder.query.filter_by(status='Pending').count()
    confirmed_count = ShopOrder.query.filter_by(status='Confirmed').count()
    completed_count = ShopOrder.query.filter_by(status='Completed').count()

    return render_template('admin_orders.html',
        orders=orders, filter_status=filter_status,
        pending_count=pending_count, confirmed_count=confirmed_count,
        completed_count=completed_count)


@shop_bp.route('/admin/orders/update/<int:id>', methods=['POST'])
@login_required
def update_order(id):
    order = ShopOrder.query.get_or_404(id)
    order.status = request.form.get('status', order.status)
    order.admin_notes = request.form.get('admin_notes', order.admin_notes)
    db.session.commit()
    flash(f'Order {order.order_number} updated to {order.status}.', 'success')
    return redirect(url_for('shop.manage_orders'))


@shop_bp.route('/admin/orders/delete/<int:id>', methods=['POST'])
@login_required
def delete_order(id):
    if not current_user.is_admin():
        flash('Only admins can delete orders.', 'danger')
        return redirect(url_for('shop.manage_orders'))
    order = ShopOrder.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted.', 'info')
    return redirect(url_for('shop.manage_orders'))
