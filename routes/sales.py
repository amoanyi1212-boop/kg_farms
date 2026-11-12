from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from sqlalchemy import func
from database import db
from models import Sale, Expense
from utils.helpers import generate_receipt_number

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')


@sales_bp.route('/')
@sales_bp.route('/daily')
@login_required
def daily_sales():
    today = date.today()
    sales = Sale.query.filter(Sale.sale_date == today).order_by(Sale.created_at.desc()).all()
    total_today = sum(s.final_amount for s in sales)
    total_items = sum(s.quantity for s in sales)
    return render_template('sales/daily_sales.html',
        sales=sales, total_today=total_today, total_items=total_items, today=today)


@sales_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        try:
            quantity = int(request.form.get('quantity', 1))
            unit_price = float(request.form.get('unit_price', 0))
            discount = float(request.form.get('discount') or 0)
            total_amount = quantity * unit_price
            final_amount = total_amount - discount

            sale = Sale(
                sale_type=request.form.get('sale_type'),
                item_description=request.form.get('item_description'),
                quantity=quantity,
                unit_price=unit_price,
                total_amount=total_amount,
                discount=discount,
                final_amount=final_amount,
                customer_name=request.form.get('customer_name'),
                customer_phone=request.form.get('customer_phone'),
                payment_method=request.form.get('payment_method', 'Cash'),
                payment_status=request.form.get('payment_status', 'Paid'),
                receipt_number=generate_receipt_number(),
                sale_date=datetime.strptime(
                    request.form.get('sale_date') or datetime.now().strftime('%Y-%m-%d'),
                    '%Y-%m-%d').date(),
                notes=request.form.get('notes'),
                sold_by=current_user.id
            )
            db.session.add(sale)
            db.session.commit()
            flash(f'Sale recorded! Receipt: {sale.receipt_number}', 'success')
            return redirect(url_for('sales.daily_sales'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('sales/add_sale.html')


@sales_bp.route('/history')
@login_required
def sales_history():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sale_type = request.args.get('sale_type', '')

    query = Sale.query
    if start_date:
        query = query.filter(Sale.sale_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Sale.sale_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if sale_type:
        query = query.filter_by(sale_type=sale_type)

    sales = query.order_by(Sale.sale_date.desc()).all()
    total_revenue = sum(s.final_amount for s in sales)
    return render_template('sales/sales_history.html',
        sales=sales, total_revenue=total_revenue,
        start_date=start_date, end_date=end_date, sale_type=sale_type)


@sales_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_sale(id):
    if not current_user.is_admin():
        flash('Only admins can delete sales.', 'danger')
        return redirect(url_for('sales.daily_sales'))
    sale = Sale.query.get_or_404(id)
    db.session.delete(sale)
    db.session.commit()
    flash('Sale deleted.', 'info')
    return redirect(url_for('sales.daily_sales'))


@sales_bp.route('/expenses')
@login_required
def expenses():
    exps = Expense.query.order_by(Expense.expense_date.desc()).limit(100).all()
    total = sum(e.amount for e in exps)
    return render_template('sales/expenses.html', expenses=exps, total=total)


@sales_bp.route('/expenses/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        try:
            exp = Expense(
                category=request.form.get('category'),
                description=request.form.get('description'),
                amount=float(request.form.get('amount', 0)),
                payment_method=request.form.get('payment_method', 'Cash'),
                expense_date=datetime.strptime(
                    request.form.get('expense_date') or datetime.now().strftime('%Y-%m-%d'),
                    '%Y-%m-%d').date(),
                notes=request.form.get('notes'),
                recorded_by=current_user.id
            )
            db.session.add(exp)
            db.session.commit()
            flash('Expense recorded.', 'success')
            return redirect(url_for('sales.expenses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('sales/add_expense.html')
