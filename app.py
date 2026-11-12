"""
K&G Farms - Farm Management System
Poultry & Livestock | Ghana | GH₵
"""
import os
from flask import Flask
from config import config
from database import init_db


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    init_db(app)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.inventory import inventory_bp
    from routes.sales import sales_bp
    from routes.feed import feed_bp
    from routes.reports import reports_bp
    from routes.shop import shop_bp
    from routes.eggs import eggs_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(eggs_bp)

    @app.template_filter('currency')
    def currency_filter(value):
        if value is None:
            return "GH₵ 0"
        return f"GH₵ {value:,.0f}"

    @app.template_filter('currency2')
    def currency2_filter(value):
        if value is None:
            return "GH₵ 0.00"
        return f"GH₵ {value:,.2f}"

    return app


# Expose 'app' at top level so both 'gunicorn app:app' and 'gunicorn wsgi:app' work!
app = create_app()

if __name__ == '__main__':
    print()
    print("=" * 50)
    print("   K&G FARMS - Management System")
    print("   Location: Ghana | Currency: GH₵")
    print("=" * 50)
    print("   Admin:  http://127.0.0.1:5000")
    print("   Shop:   http://127.0.0.1:5000/shop")
    print("   Login:  admin / admin123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
