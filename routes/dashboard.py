from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import func
from database import db
from models import (User, Poultry, Livestock, FeedInventory,
                    FeedLog, Sale, Expense, MortalityLog)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    this_month_start = today.replace(day=1)

    total_poultry = db.session.query(func.sum(Poultry.quantity)).scalar() or 0
    poultry_by_type = db.session.query(
        Poultry.bird_type, func.sum(Poultry.quantity)
    ).group_by(Poultry.bird_type).all()
    available_poultry = db.session.query(func.sum(Poultry.quantity)).filter(
        Poultry.status == 'Available'
    ).scalar() or 0

    total_livestock = db.session.query(func.sum(Livestock.quantity)).scalar() or 0
    livestock_by_type = db.session.query(
        Livestock.animal_type, func.sum(Livestock.quantity)
    ).group_by(Livestock.animal_type).all()
    available_livestock = db.session.query(func.sum(Livestock.quantity)).filter(
        Livestock.status == 'Available'
    ).scalar() or 0
    goats_count = db.session.query(func.sum(Livestock.quantity)).filter(
        Livestock.animal_type.ilike('%goat%')
    ).scalar() or 0
    sheep_count = db.session.query(func.sum(Livestock.quantity)).filter(
        Livestock.animal_type.ilike('%sheep%') |
        Livestock.animal_type.ilike('%ram%') |
        Livestock.animal_type.ilike('%ewe%') |
        Livestock.animal_type.ilike('%lamb%')
    ).scalar() or 0

    total_feed_items = FeedInventory.query.count()
    low_stock_feeds = FeedInventory.query.filter(
        FeedInventory.quantity_in_stock <= FeedInventory.reorder_level
    ).all()
    total_feed_value = db.session.query(
        func.sum(FeedInventory.quantity_in_stock * FeedInventory.unit_cost)
    ).scalar() or 0.0
    today_feed_given = db.session.query(func.sum(FeedLog.quantity_given)).filter(
        FeedLog.date_given == today
    ).scalar() or 0.0

    today_sales = Sale.query.filter(Sale.sale_date == today).all()
    today_revenue = db.session.query(func.sum(Sale.final_amount)).filter(
        Sale.sale_date == today
    ).scalar() or 0.0
    month_revenue = db.session.query(func.sum(Sale.final_amount)).filter(
        Sale.sale_date >= this_month_start
    ).scalar() or 0.0
    total_sales_count = Sale.query.count()

    today_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.expense_date == today
    ).scalar() or 0.0
    month_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.expense_date >= this_month_start
    ).scalar() or 0.0

    today_deaths = db.session.query(func.sum(MortalityLog.quantity_dead)).filter(
        MortalityLog.date_of_death == today
    ).scalar() or 0
    month_deaths = db.session.query(func.sum(MortalityLog.quantity_dead)).filter(
        MortalityLog.date_of_death >= this_month_start
    ).scalar() or 0

    today_profit = today_revenue - today_expenses
    month_profit = month_revenue - month_expenses

    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    recent_mortality = MortalityLog.query.order_by(MortalityLog.created_at.desc()).limit(5).all()
    recent_feed_logs = FeedLog.query.order_by(FeedLog.created_at.desc()).limit(5).all()

    sick_livestock = Livestock.query.filter(
        Livestock.health_status.ilike('%sick%') |
        Livestock.health_status.ilike('%quarantine%')
    ).all()

    return render_template('dashboard.html',
        total_poultry=total_poultry, available_poultry=available_poultry,
        poultry_by_type=poultry_by_type,
        total_livestock=total_livestock, available_livestock=available_livestock,
        livestock_by_type=livestock_by_type,
        goats_count=goats_count, sheep_count=sheep_count,
        total_feed_items=total_feed_items, low_stock_feeds=low_stock_feeds,
        total_feed_value=total_feed_value, today_feed_given=today_feed_given,
        today_sales=today_sales, today_revenue=today_revenue,
        month_revenue=month_revenue, total_sales_count=total_sales_count,
        today_expenses=today_expenses, month_expenses=month_expenses,
        today_deaths=today_deaths, month_deaths=month_deaths,
        today_profit=today_profit, month_profit=month_profit,
        recent_sales=recent_sales, recent_mortality=recent_mortality,
        recent_feed_logs=recent_feed_logs, sick_livestock=sick_livestock,
        today=today
    )
