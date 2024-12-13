import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy.orm import DeclarativeBase
from swagger import swagger_config

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
babel = Babel()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.Config')
        
    # Add security headers in production
    @app.after_request
    def add_security_headers(response):
        if app.config.get('SECURITY_HEADERS'):
            for header, value in app.config['SECURITY_HEADERS'].items():
                response.headers[header] = value
        return response
    
    # Initialize extensions
    db.init_app(app)
    babel.init_app(app)
    
    def get_locale():
        return 'cs'
    
    babel.select_locale_func = get_locale
    
    # Register Swagger UI blueprint
    SWAGGER_URL = '/swagger'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Phone Management System API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    @app.route('/swagger.json')
    def swagger():
        return jsonify(swagger_config())
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
            
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {str(e)}")
            raise
        
    return app

app = create_app()

# Import and register blueprints after app is created to avoid circular imports
def register_blueprints(app):
    from routes.devices import devices as devices_blueprint
    app.register_blueprint(devices_blueprint, url_prefix='/devices')

    @app.route('/')
    def index():
        return redirect(url_for('devices.list_devices'))

register_blueprints(app)