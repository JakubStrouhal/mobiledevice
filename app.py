import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_babel import Babel
from flask_swagger_ui import get_swaggerui_blueprint
from flask_wtf.csrf import CSRFProtect
from swagger import swagger_config
from sqlalchemy import text as sqlalchemy_text
from extensions import db

csrf = CSRFProtect()

# Configure logging
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        handlers=[
            RotatingFileHandler('app.log', maxBytes=10000000, backupCount=10),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.DEBUG)

babel = Babel()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    # Always use production config for deployment
    app.config.from_object('config.ProductionConfig')
    # Ensure debug mode is disabled
    app.debug = False
        
    # Add security headers in production
    @app.after_request
    def add_security_headers(response):
        if app.config.get('SECURITY_HEADERS'):
            for header, value in app.config['SECURITY_HEADERS'].items():
                response.headers[header] = value
        return response
    
    # Initialize extensions
    from extensions import db
    db.init_app(app)
    babel.init_app(app)
    csrf.init_app(app)
    
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
        logging.error(f"Internal Server Error: {str(error)}")
        return render_template('errors/500.html'), 500

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logging.info("Database tables created successfully")
            
            # Verify critical tables exist
            with db.engine.connect() as conn:
                tables = ['users', 'phones', 'device_make', 'device_model', 'phone_assignments']
                for table in tables:
                    result = conn.execute(sqlalchemy_text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"))
                    exists = result.scalar()
                    if exists:
                        logging.info(f"Table '{table}' exists")
                    else:
                        logging.error(f"Table '{table}' was not created")
                        raise Exception(f"Critical table '{table}' is missing")
                        
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

if __name__ == '__main__':
    # Production settings with proper host binding
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)