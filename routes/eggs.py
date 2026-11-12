from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from database import db
from models import EggInventory

eggs_bp = Blueprint('eggs', __name__, url_prefix='/eggs')

EGG_TYPES = ["Chicken (Layer)", "Turkey", "Duck", "Guinea Fowl", "Quail", "Cockerel (Fertilized)"]
EGG_SIZES = ["Peewee", "Small", "Medium", "Large", "Extra Large", "Jumbo"]
EGG_COLORS = ["White", "Brown", "Cream", "Speckled", "Blue/Green"]
EGG_GRADES = ["Grade A (Premium)", "Grade B (Standard)", "Grade C (Cracked/Cooking)"]
EGG_STATUS = ["Available", "Reserved", "Sold", "Broken", "Expired"]


@eggs_bp.route('/')
@eggs_bp.route('/inventory')
@login_required
def inventory():
    filter_type = request.args.get('type', '')
    filter_status = request.args.get('status', '')

    query = EggInventory.query
    if filter_type:
        query = query.filter_by(egg_type=filter_type)
    if filter_status:
        query = query.filter_by(status=filter_status)

    eggs = query.order_by(EggInventory.collection_date.desc()).all()
    total_crates = sum(e.crates_in_stock for e in eggs)
    total_loose = sum(e.loose_eggs for e in eggs)
    total_eggs = sum(e.total_eggs for e in eggs)
    total_value = sum(e.total_value for e in eggs)
    low_stock = [e for e in eggs if e.is_low_stock and e.status == 'Available']
    expiring_soon = [e for e in eggs if e.expiry_date and
                     (e.expiry_date - date.today()).days <= 7 and
                     (e.expiry_date - date.today()).days >= 0]

    return render_template('eggs/inventory.html',
        eggs=eggs, total_crates=total_crates, total_loose=total_loose,
        total_eggs=total_eggs, total_value=total_value,
        low_stock=low_stock, expiring_soon=expiring_soon,
        egg_types=EGG_TYPES, egg_statuses=EGG_STATUS,
        filter_type=filter_type, filter_status=filter_status)


@eggs_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_egg():
    if request.method == 'POST':
        try:
            expiry = request.form.get('expiry_date')
            collection = request.form.get('collection_date') or datetime.now().strftime('%Y-%m-%d')

            # Auto-set expiry to 28 days from collection if not provided
            if not expiry:
                col_date = datetime.strptime(collection, '%Y-%m-%d').date()
                expiry_date = col_date + timedelta(days=28)
            else:
                expiry_date = datetime.strptime(expiry, '%Y-%m-%d').date()

            egg = EggInventory(
                egg_type=request.form.get('egg_type'),
                egg_size=request.form.get('egg_size'),
                egg_color=request.form.get('egg_color'),
                grade=request.form.get('grade'),
                source_batch=request.form.get('source_batch'),
                crates_in_stock=int(request.form.get('crates_in_stock', 0)),
                loose_eggs=int(request.form.get('loose_eggs', 0)),
                price_per_crate=float(request.form.get('price_per_crate') or 0),
                price_per_egg=float(request.form.get('price_per_egg') or 0),
                reorder_level=int(request.form.get('reorder_level') or 10),
                collection_date=datetime.strptime(collection, '%Y-%m-%d').date(),
                expiry_date=expiry_date,
                storage_location=request.form.get('storage_location'),
                status=request.form.get('status', 'Available'),
                notes=request.form.get('notes'),
                created_by=current_user.id
            )
            db.session.add(egg)
            db.session.commit()
            flash(f'Added {egg.crates_in_stock} crates + {egg.loose_eggs} loose {egg.egg_type} eggs.', 'success')
            return redirect(url_for('eggs.inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('eggs/add_egg.html',
        egg_types=EGG_TYPES, sizes=EGG_SIZES, colors=EGG_COLORS,
        grades=EGG_GRADES, statuses=EGG_STATUS)


@eggs_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_egg(id):
    egg = EggInventory.query.get_or_404(id)

    if request.method == 'POST':
        try:
            egg.egg_type = request.form.get('egg_type')
            egg.egg_size = request.form.get('egg_size')
            egg.egg_color = request.form.get('egg_color')
            egg.grade = request.form.get('grade')
            egg.source_batch = request.form.get('source_batch')
            egg.crates_in_stock = int(request.form.get('crates_in_stock', 0))
            egg.loose_eggs = int(request.form.get('loose_eggs', 0))
            egg.price_per_crate = float(request.form.get('price_per_crate') or 0)
            egg.price_per_egg = float(request.form.get('price_per_egg') or 0)
            egg.reorder_level = int(request.form.get('reorder_level') or 10)
            egg.storage_location = request.form.get('storage_location')
            egg.status = request.form.get('status')
            egg.notes = request.form.get('notes')

            expiry = request.form.get('expiry_date')
            if expiry:
                egg.expiry_date = datetime.strptime(expiry, '%Y-%m-%d').date()

            db.session.commit()
            flash('Egg record updated!', 'success')
            return redirect(url_for('eggs.inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('eggs/edit_egg.html', egg=egg,
        egg_types=EGG_TYPES, sizes=EGG_SIZES, colors=EGG_COLORS,
        grades=EGG_GRADES, statuses=EGG_STATUS)


@eggs_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_egg(id):
    if not current_user.is_admin():
        flash('Only admins can delete records.', 'danger')
        return redirect(url_for('eggs.inventory'))
    egg = EggInventory.query.get_or_404(id)
    db.session.delete(egg)
    db.session.commit()
    flash('Egg record deleted.', 'info')
    return redirect(url_for('eggs.inventory'))


@eggs_bp.route('/collect', methods=['GET', 'POST'])
@login_required
def daily_collection():
    """Quick daily egg collection log"""
    if request.method == 'POST':
        try:
            egg = EggInventory(
                egg_type=request.form.get('egg_type', 'Chicken (Layer)'),
                egg_size='Medium',
                egg_color=request.form.get('egg_color', 'Brown'),
                grade='Grade A (Premium)',
                source_batch=request.form.get('source_batch'),
                crates_in_stock=int(request.form.get('crates_in_stock', 0)),
                loose_eggs=int(request.form.get('loose_eggs', 0)),
                collection_date=date.today(),
                expiry_date=date.today() + timedelta(days=28),
                status='Available',
                notes=f"Daily collection - {date.today().strftime('%b %d, %Y')}",
                created_by=current_user.id
            )
            db.session.add(egg)
            db.session.commit()
            flash(f'Logged todays collection: {egg.crates_in_stock} crates + {egg.loose_eggs} loose eggs', 'success')
            return redirect(url_for('eggs.inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('eggs/collect.html', egg_types=EGG_TYPES, colors=EGG_COLORS)
