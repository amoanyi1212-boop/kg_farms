from datetime import datetime, date
from flask_login import UserMixin
from database import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default='staff')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Poultry(db.Model):
    __tablename__ = 'poultry'
    id = db.Column(db.Integer, primary_key=True)
    bird_type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=True)
    batch_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    age_weeks = db.Column(db.Integer, nullable=True)
    avg_weight_kg = db.Column(db.Float, nullable=True)
    unit_price = db.Column(db.Float, nullable=True)
    housing = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='Available')
    date_acquired = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator = db.relationship('User', backref='poultry_entries')

    @property
    def total_value(self):
        if self.unit_price and self.quantity:
            return self.quantity * self.unit_price
        return 0.0


class Livestock(db.Model):
    __tablename__ = 'livestock'
    id = db.Column(db.Integer, primary_key=True)
    animal_type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=True)
    tag_id = db.Column(db.String(50), unique=True, nullable=True)
    batch_name = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    gender = db.Column(db.String(10), nullable=True)
    age_months = db.Column(db.Integer, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    color_markings = db.Column(db.String(100), nullable=True)
    unit_price = db.Column(db.Float, nullable=True)
    health_status = db.Column(db.String(50), default='Healthy')
    housing = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='Available')
    date_acquired = db.Column(db.Date, default=date.today)
    vaccination_status = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator = db.relationship('User', backref='livestock_entries')

    @property
    def total_value(self):
        if self.unit_price and self.quantity:
            return self.quantity * self.unit_price
        return 0.0


class EggInventory(db.Model):
    """Egg stock tracking with crate & piece counts"""
    __tablename__ = 'egg_inventory'
    id = db.Column(db.Integer, primary_key=True)
    egg_type = db.Column(db.String(50), nullable=False)  # Chicken, Turkey, Duck, Guinea, Quail
    egg_size = db.Column(db.String(20), nullable=True)  # Small, Medium, Large, Extra Large, Jumbo
    egg_color = db.Column(db.String(30), nullable=True)  # White, Brown, Speckled
    grade = db.Column(db.String(50), nullable=True)  # Grade A (Premium), etc.
    source_batch = db.Column(db.String(100), nullable=True)  # Which poultry batch laid them
    crates_in_stock = db.Column(db.Integer, nullable=False, default=0)  # 1 crate = 30 eggs
    loose_eggs = db.Column(db.Integer, nullable=False, default=0)  # Eggs not in crate
    price_per_crate = db.Column(db.Float, nullable=True)
    price_per_egg = db.Column(db.Float, nullable=True)
    reorder_level = db.Column(db.Integer, default=10)  # Alert when crates drop below
    collection_date = db.Column(db.Date, default=date.today)
    expiry_date = db.Column(db.Date, nullable=True)
    storage_location = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='Available')  # Available, Sold, Broken, Expired
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator = db.relationship('User', backref='egg_entries')

    @property
    def total_eggs(self):
        return (self.crates_in_stock * 30) + self.loose_eggs

    @property
    def total_value(self):
        crate_value = (self.crates_in_stock * (self.price_per_crate or 0))
        loose_value = (self.loose_eggs * (self.price_per_egg or 0))
        return crate_value + loose_value

    @property
    def is_low_stock(self):
        return self.crates_in_stock <= self.reorder_level

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False


class FeedInventory(db.Model):
    __tablename__ = 'feed_inventory'
    id = db.Column(db.Integer, primary_key=True)
    feed_name = db.Column(db.String(100), nullable=False)
    feed_category = db.Column(db.String(50), nullable=True)
    supplier = db.Column(db.String(150), nullable=True)
    quantity_in_stock = db.Column(db.Float, nullable=False, default=0.0)
    unit = db.Column(db.String(30), default='kg')
    unit_cost = db.Column(db.Float, nullable=True)
    reorder_level = db.Column(db.Float, default=50.0)
    batch_number = db.Column(db.String(50), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    storage_location = db.Column(db.String(100), nullable=True)
    date_received = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator = db.relationship('User', backref='feed_entries')

    @property
    def total_value(self):
        if self.unit_cost and self.quantity_in_stock:
            return self.quantity_in_stock * self.unit_cost
        return 0.0

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level


class FeedLog(db.Model):
    __tablename__ = 'feed_log'
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed_inventory.id'), nullable=False)
    target_group = db.Column(db.String(100), nullable=False)
    animal_type = db.Column(db.String(50), nullable=False)
    quantity_given = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), default='kg')
    feeding_time = db.Column(db.String(20), nullable=True)
    date_given = db.Column(db.Date, default=date.today)
    fed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    feed = db.relationship('FeedInventory', backref='consumption_logs')
    feeder = db.relationship('User', backref='feed_logs')


class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    sale_type = db.Column(db.String(20), nullable=False)
    item_description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)
    customer_name = db.Column(db.String(150), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    payment_method = db.Column(db.String(30), default='Cash')
    payment_status = db.Column(db.String(20), default='Paid')
    receipt_number = db.Column(db.String(50), unique=True, nullable=True)
    sale_date = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    sold_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller = db.relationship('User', backref='sales_made')


class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(30), default='Cash')
    expense_date = db.Column(db.Date, default=date.today)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recorder = db.relationship('User', backref='expenses_recorded')


class MortalityLog(db.Model):
    __tablename__ = 'mortality_log'
    id = db.Column(db.Integer, primary_key=True)
    animal_category = db.Column(db.String(20), nullable=False)
    animal_type = db.Column(db.String(50), nullable=False)
    batch_or_tag = db.Column(db.String(100), nullable=True)
    quantity_dead = db.Column(db.Integer, nullable=False, default=1)
    suspected_cause = db.Column(db.String(200), nullable=True)
    date_of_death = db.Column(db.Date, default=date.today)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reporter = db.relationship('User', backref='mortality_reports')


class ShopOrder(db.Model):
    __tablename__ = 'shop_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120), nullable=True)
    customer_location = db.Column(db.String(200), nullable=True)
    item_type = db.Column(db.String(20), nullable=False)
    item_description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    preferred_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Pending')
    admin_notes = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
