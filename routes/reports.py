from flask import Blueprint, render_template, request
from flask_login import login_required
from datetime import datetime, date, timedelta
from sqlalchemy import func
from database import db
from models import Sale, Expense, Poultry, Livestock, FeedInventory, FeedLog, MortalityLog

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@reports_bp.route('/summary')
@login_required
def summary():
    today = date.today()
    month_start = today.replace(day=1)

    total_revenue = db.session.query(func.sum(Sale.final_amount)).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    total_profit = total_revenue - total_expenses

    total_birds = db.session.query(func.sum(Poultry.quantity)).scalar() or 0
    total_animals = db.session.query(func.sum(Livestock.quantity)).scalar() or 0
    total_deaths = db.session.query(func.sum(MortalityLog.quantity_dead)).scalar() or 0

    month_revenue = db.session.query(func.sum(Sale.final_amount)).filter(
        Sale.sale_date >= month_start).scalar() or 0
    month_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.expense_date >= month_start).scalar() or 0

    return render_template('reports/summary.html',
        total_revenue=total_revenue, total_expenses=total_expenses,
        total_profit=total_profit, total_birds=total_birds,
        total_animals=total_animals, total_deaths=total_deaths,
        month_revenue=month_revenue, month_expenses=month_expenses,
        month_profit=month_revenue - month_expenses, today=today)


@reports_bp.route('/daily')
@login_required
def daily_report():
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    report_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    sales = Sale.query.filter(Sale.sale_date == report_date).all()
    expenses = Expense.query.filter(Expense.expense_date == report_date).all()
    feed_logs = FeedLog.query.filter(FeedLog.date_given == report_date).all()
    deaths = MortalityLog.query.filter(MortalityLog.date_of_death == report_date).all()

    total_revenue = sum(s.final_amount for s in sales)
    total_expenses = sum(e.amount for e in expenses)
    total_feed = sum(f.quantity_given for f in feed_logs)
    total_deaths = sum(d.quantity_dead for d in deaths)

    return render_template('reports/daily_report.html',
        sales=sales, expenses=expenses, feed_logs=feed_logs, deaths=deaths,
        total_revenue=total_revenue, total_expenses=total_expenses,
        total_feed=total_feed, total_deaths=total_deaths,
        profit=total_revenue - total_expenses,
        report_date=report_date, selected_date=selected_date)


@reports_bp.route('/monthly')
@login_required
def monthly_report():
    month = request.args.get('month', date.today().strftime('%Y-%m'))
    year, mon = map(int, month.split('-'))
    start = date(year, mon, 1)
    if mon == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, mon + 1, 1) - timedelta(days=1)

    sales = Sale.query.filter(Sale.sale_date.between(start, end)).all()
    expenses = Expense.query.filter(Expense.expense_date.between(start, end)).all()
    deaths = MortalityLog.query.filter(MortalityLog.date_of_death.between(start, end)).all()

    total_revenue = sum(s.final_amount for s in sales)
    total_expenses = sum(e.amount for e in expenses)

    sales_by_type = {}
    for s in sales:
        sales_by_type[s.sale_type] = sales_by_type.get(s.sale_type, 0) + s.final_amount

    expenses_by_cat = {}
    for e in expenses:
        expenses_by_cat[e.category] = expenses_by_cat.get(e.category, 0) + e.amount

    return render_template('reports/monthly_report.html',
        month=month, start=start, end=end,
        sales=sales, expenses=expenses, deaths=deaths,
        total_revenue=total_revenue, total_expenses=total_expenses,
        profit=total_revenue - total_expenses,
        sales_by_type=sales_by_type, expenses_by_cat=expenses_by_cat,
        total_deaths=sum(d.quantity_dead for d in deaths))
