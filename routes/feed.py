from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from database import db
from models import FeedInventory, FeedLog
from config import Config

feed_bp = Blueprint('feed', __name__, url_prefix='/feed')


@feed_bp.route('/')
@feed_bp.route('/inventory')
@login_required
def feed_inventory():
    feeds = FeedInventory.query.order_by(FeedInventory.feed_name).all()
    total_value = sum(f.total_value for f in feeds)
    low_stock = [f for f in feeds if f.is_low_stock]
    return render_template('feed/feed_inventory.html',
        feeds=feeds, total_value=total_value, low_stock=low_stock)


@feed_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_feed():
    if request.method == 'POST':
        try:
            expiry = request.form.get('expiry_date')
            feed = FeedInventory(
                feed_name=request.form.get('feed_name'),
                feed_category=request.form.get('feed_category'),
                supplier=request.form.get('supplier'),
                quantity_in_stock=float(request.form.get('quantity_in_stock', 0)),
                unit=request.form.get('unit', 'kg'),
                unit_cost=float(request.form.get('unit_cost') or 0),
                reorder_level=float(request.form.get('reorder_level') or 50),
                batch_number=request.form.get('batch_number'),
                expiry_date=datetime.strptime(expiry, '%Y-%m-%d').date() if expiry else None,
                storage_location=request.form.get('storage_location'),
                date_received=datetime.strptime(
                    request.form.get('date_received') or datetime.now().strftime('%Y-%m-%d'),
                    '%Y-%m-%d').date(),
                notes=request.form.get('notes'),
                created_by=current_user.id
            )
            db.session.add(feed)
            db.session.commit()
            flash(f'Added {feed.feed_name} to feed inventory!', 'success')
            return redirect(url_for('feed.feed_inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('feed/add_feed.html',
        feed_types=Config.FEED_TYPES, units=Config.FEED_UNITS)


@feed_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_feed(id):
    feed = FeedInventory.query.get_or_404(id)
    if request.method == 'POST':
        try:
            feed.feed_name = request.form.get('feed_name')
            feed.feed_category = request.form.get('feed_category')
            feed.supplier = request.form.get('supplier')
            feed.quantity_in_stock = float(request.form.get('quantity_in_stock', 0))
            feed.unit = request.form.get('unit')
            feed.unit_cost = float(request.form.get('unit_cost') or 0)
            feed.reorder_level = float(request.form.get('reorder_level') or 50)
            feed.storage_location = request.form.get('storage_location')
            feed.notes = request.form.get('notes')
            db.session.commit()
            flash('Feed updated!', 'success')
            return redirect(url_for('feed.feed_inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('feed/edit_feed.html', feed=feed,
        feed_types=Config.FEED_TYPES, units=Config.FEED_UNITS)


@feed_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_feed(id):
    if not current_user.is_admin():
        flash('Only admins can delete feed records.', 'danger')
        return redirect(url_for('feed.feed_inventory'))
    feed = FeedInventory.query.get_or_404(id)
    db.session.delete(feed)
    db.session.commit()
    flash('Feed deleted.', 'info')
    return redirect(url_for('feed.feed_inventory'))


@feed_bp.route('/log')
@login_required
def feed_log():
    logs = FeedLog.query.order_by(FeedLog.date_given.desc()).limit(200).all()
    today_total = sum(l.quantity_given for l in logs if l.date_given == date.today())
    return render_template('feed/feed_log.html', logs=logs, today_total=today_total)


@feed_bp.route('/log/add', methods=['GET', 'POST'])
@login_required
def add_feed_log():
    if request.method == 'POST':
        try:
            feed_id = int(request.form.get('feed_id'))
            qty = float(request.form.get('quantity_given', 0))
            feed = FeedInventory.query.get_or_404(feed_id)

            if qty > feed.quantity_in_stock:
                flash(f'Not enough {feed.feed_name} in stock! Only {feed.quantity_in_stock} {feed.unit} available.', 'danger')
                return redirect(url_for('feed.add_feed_log'))

            log = FeedLog(
                feed_id=feed_id,
                target_group=request.form.get('target_group'),
                animal_type=request.form.get('animal_type'),
                quantity_given=qty,
                unit=feed.unit,
                feeding_time=request.form.get('feeding_time'),
                date_given=datetime.strptime(
                    request.form.get('date_given') or datetime.now().strftime('%Y-%m-%d'),
                    '%Y-%m-%d').date(),
                notes=request.form.get('notes'),
                fed_by=current_user.id
            )
            feed.quantity_in_stock -= qty
            db.session.add(log)
            db.session.commit()
            flash(f'Fed {qty} {feed.unit} of {feed.feed_name} to {log.target_group}.', 'success')
            return redirect(url_for('feed.feed_log'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    feeds = FeedInventory.query.filter(FeedInventory.quantity_in_stock > 0).all()
    return render_template('feed/add_feed_log.html', feeds=feeds)


@feed_bp.route('/schedule')
@login_required
def feed_schedule():
    feeds = FeedInventory.query.all()
    return render_template('feed/feed_schedule.html', feeds=feeds)
