from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from database import db
from models import Poultry, Livestock, MortalityLog
from config import Config

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')


# ---------------- POULTRY ----------------
@inventory_bp.route('/poultry')
@login_required
def poultry():
    filter_status = request.args.get('status', '')
    filter_type = request.args.get('type', '')

    query = Poultry.query
    if filter_status:
        query = query.filter_by(status=filter_status)
    if filter_type:
        query = query.filter_by(bird_type=filter_type)

    birds = query.order_by(Poultry.created_at.desc()).all()
    total_birds = sum(b.quantity for b in birds)
    total_value = sum(b.total_value for b in birds)

    return render_template('inventory/poultry.html',
        birds=birds, total_birds=total_birds, total_value=total_value,
        bird_types=Config.POULTRY_TYPES, stock_statuses=Config.STOCK_STATUS,
        filter_status=filter_status, filter_type=filter_type)


@inventory_bp.route('/poultry/add', methods=['GET', 'POST'])
@login_required
def add_poultry():
    if request.method == 'POST':
        try:
            bird = Poultry(
                bird_type=request.form.get('bird_type'),
                breed=request.form.get('breed'),
                batch_name=request.form.get('batch_name'),
                quantity=int(request.form.get('quantity', 0)),
                age_weeks=int(request.form.get('age_weeks') or 0),
                avg_weight_kg=float(request.form.get('avg_weight_kg') or 0),
                unit_price=float(request.form.get('unit_price') or 0),
                housing=request.form.get('housing'),
                status=request.form.get('status', 'Available'),
                date_acquired=datetime.strptime(
                    request.form.get('date_acquired') or datetime.now().strftime('%Y-%m-%d'),
                    '%Y-%m-%d').date(),
                notes=request.form.get('notes'),
                created_by=current_user.id
            )
            db.session.add(bird)
            db.session.commit()
            flash(f'Added {bird.quantity} {bird.bird_type} to inventory!', 'success')
            return redirect(url_for('inventory.poultry'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('inventory/add_stock.html',
        stock_type='poultry', types=Config.POULTRY_TYPES,
        statuses=Config.STOCK_STATUS)


@inventory_bp.route('/poultry/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_poultry(id):
    bird = Poultry.query.get_or_404(id)
    if request.method == 'POST':
        try:
            bird.bird_type = request.form.get('bird_type')
            bird.breed = request.form.get('breed')
            bird.batch_name = request.form.get('batch_name')
            bird.quantity = int(request.form.get('quantity', 0))
            bird.age_weeks = int(request.form.get('age_weeks') or 0)
            bird.avg_weight_kg = float(request.form.get('avg_weight_kg') or 0)
            bird.unit_price = float(request.form.get('unit_price') or 0)
            bird.housing = request.form.get('housing')
            bird.status = request.form.get('status')
            bird.notes = request.form.get('notes')
            db.session.commit()
            flash('Poultry record updated!', 'success')
            return redirect(url_for('inventory.poultry'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('inventory/edit_stock.html',
        stock=bird, stock_type='poultry',
        types=Config.POULTRY_TYPES, statuses=Config.STOCK_STATUS)


@inventory_bp.route('/poultry/delete/<int:id>', methods=['POST'])
@login_required
def delete_poultry(id):
    if not current_user.is_admin():
        flash('Only admins can delete records.', 'danger')
        return redirect(url_for('inventory.poultry'))
    bird = Poultry.query.get_or_404(id)
    db.session.delete(bird)
    db.session.commit()
    flash('Poultry record deleted.', 'info')
    return redirect(url_for('inventory.poultry'))


# ---------------- LIVESTOCK ----------------
@inventory_bp.route('/livestock')
@login_required
def livestock():
    filter_status = request.args.get('status', '')
    filter_type = request.args.get('type', '')

    query = Livestock.query
    if filter_status:
        query = query.filter_by(status=filter_status)
    if filter_type:
        query = query.filter_by(animal_type=filter_type)

    animals = query.order_by(Livestock.created_at.desc()).all()
    total_animals = sum(a.quantity for a in animals)
    total_value = sum(a.total_value for a in animals)

    return render_template('inventory/livestock.html',
        animals=animals, total_animals=total_animals, total_value=total_value,
        animal_types=Config.LIVESTOCK_TYPES, stock_statuses=Config.STOCK_STATUS,
        filter_status=filter_status, filter_type=filter_type)


@inventory_bp.route('/livestock/add', methods=['GET', 'POST'])
@login_required
def add_livestock():
    if request.method == 'POST':
        try:
            animal = Livestock(
                animal_type=request.form.get('animal_type'),
                breed=request.form.get('breed'),
                tag_id=request.form.get('tag_id') or None,
                batch_name=request.form.get('batch_name'),
                quantity=int(request.form.get('quantity', 1)),
                gender=request.form.get('gender'),
                age_months=int(request.form.get('age_months') or 0),
                weight_kg=float(request.form.get('weight_kg') or 0),
                color_markings=request.form.get('color_markings'),
                unit_price=float(request.form.get('unit_price') or 0),
                health_status=request.form.get('health_status', 'Healthy'),
                housing=request.form.get('housing'),
                status=request.form.get('status', 'Available'),
                vaccination_status=request.form.get('vaccination_status'),
                date_acquired=datetime.strptime(
                    request.form.get('date_acquired') or datetime.now().strftime('%Y-%m-%d'),
                    '%Y-%m-%d').date(),
                notes=request.form.get('notes'),
                created_by=current_user.id
            )
            db.session.add(animal)
            db.session.commit()
            flash(f'Added {animal.quantity} {animal.animal_type} to inventory!', 'success')
            return redirect(url_for('inventory.livestock'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('inventory/add_stock.html',
        stock_type='livestock', types=Config.LIVESTOCK_TYPES,
        statuses=Config.STOCK_STATUS)


@inventory_bp.route('/livestock/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_livestock(id):
    animal = Livestock.query.get_or_404(id)
    if request.method == 'POST':
        try:
            animal.animal_type = request.form.get('animal_type')
            animal.breed = request.form.get('breed')
            animal.tag_id = request.form.get('tag_id') or None
            animal.batch_name = request.form.get('batch_name')
            animal.quantity = int(request.form.get('quantity', 1))
            animal.gender = request.form.get('gender')
            animal.age_months = int(request.form.get('age_months') or 0)
            animal.weight_kg = float(request.form.get('weight_kg') or 0)
            animal.color_markings = request.form.get('color_markings')
            animal.unit_price = float(request.form.get('unit_price') or 0)
            animal.health_status = request.form.get('health_status')
            animal.housing = request.form.get('housing')
            animal.status = request.form.get('status')
            animal.vaccination_status = request.form.get('vaccination_status')
            animal.notes = request.form.get('notes')
            db.session.commit()
            flash('Livestock record updated!', 'success')
            return redirect(url_for('inventory.livestock'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('inventory/edit_stock.html',
        stock=animal, stock_type='livestock',
        types=Config.LIVESTOCK_TYPES, statuses=Config.STOCK_STATUS)


@inventory_bp.route('/livestock/delete/<int:id>', methods=['POST'])
@login_required
def delete_livestock(id):
    if not current_user.is_admin():
        flash('Only admins can delete records.', 'danger')
        return redirect(url_for('inventory.livestock'))
    animal = Livestock.query.get_or_404(id)
    db.session.delete(animal)
    db.session.commit()
    flash('Livestock record deleted.', 'info')
    return redirect(url_for('inventory.livestock'))


# ---------------- MORTALITY ----------------
@inventory_bp.route('/mortality')
@login_required
def mortality():
    logs = MortalityLog.query.order_by(MortalityLog.date_of_death.desc()).all()
    total_deaths = sum(m.quantity_dead for m in logs)
    return render_template('inventory/mortality.html',
        logs=logs, total_deaths=total_deaths)


@inventory_bp.route('/mortality/add', methods=['GET', 'POST'])
@login_required
def add_mortality():
    if request.method == 'POST':
        try:
            log = MortalityLog(
                animal_category=request.form.get('animal_category'),
                animal_type=request.form.get('animal_type'),
                batch_or_tag=request.form.get('batch_or_tag'),
                quantity_dead=int(request.form.get('quantity_dead', 1)),
                suspected_cause=request.form.get('suspected_cause'),
                date_of_death=datetime.strptime(
                    request.form.get('date_of_death') or datetime.now().strftime('%Y-%m-%d'),
                    '%Y-%m-%d').date(),
                notes=request.form.get('notes'),
                reported_by=current_user.id
            )
            db.session.add(log)
            db.session.commit()
            flash('Mortality logged.', 'success')
            return redirect(url_for('inventory.mortality'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('inventory/add_mortality.html')
