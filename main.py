from app import app
import logging
import os

if __name__ == "__main__":
    # Set up logging based on environment
    log_level = logging.INFO if os.environ.get('FLASK_ENV') == 'production' else logging.DEBUG
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Run the application
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host="0.0.0.0", port=5000, debug=debug)
