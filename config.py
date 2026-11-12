import os
from datetime import timedelta

class Config:
    """Base configuration for K&G Farms"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kg-farms-ghana-production-secret-key-2026'
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Handle Render / PostgreSQL or default SQLite
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Fix SQLAlchemy compatibility for Render (postgres:// -> postgresql://)
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        # Force psycopg2 driver so Render does not look for psycopg (v3)
        if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'kg_farms.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Business Information (Ghana)
    FARM_NAME = "K&G Farms"
    FARM_CURRENCY = "GH\u20b5"
    FARM_CURRENCY_CODE = "GHS"
    FARM_LOCATION = "Ghana"
    FARM_PHONE = "054 812 5064"
    FARM_EMAIL = "kgfarms.business@gmail.com"
    FARM_WHATSAPP = "https://wa.me/233548125064"

    # Presets
    POULTRY_TYPES = ["Broiler", "Layer", "Turkey", "Duck", "Guinea Fowl", "Cockerel", "Pullet"]
    LIVESTOCK_TYPES = ["Goat", "Sheep", "Ram", "Ewe", "Billy Goat", "Nanny Goat", "Lamb", "Kid"]
    FEED_TYPES = [
        "Starter Feed", "Grower Feed", "Finisher Feed", "Layer Mash",
        "Broiler Starter", "Broiler Finisher", "Goat Feed", "Sheep Feed",
        "Mineral Supplement", "Corn", "Soya Meal", "Fish Meal", "Wheat Offal",
        "Groundnut Cake", "Bone Meal", "Oyster Shell"
    ]
    FEED_UNITS = ["kg", "bags (25kg)", "bags (50kg)", "tons"]
    WEIGHT_UNITS = ["kg", "lbs"]
    STOCK_STATUS = ["Available", "Reserved", "Sold", "Dead", "Quarantined"]
    EXPENSE_CATEGORIES = [
        "Feed", "Veterinary", "Labor", "Transport", "Equipment",
        "Utilities", "Medication", "Maintenance", "Other"
    ]
    PAYMENT_METHODS = ["Cash", "Mobile Money", "Bank Transfer", "POS", "Credit"]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # In production on Render with HTTPS enabled:
    # SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
