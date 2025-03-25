#app.py
from flask import Flask
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from flask_app.api.auth import auth_bp  # Import the auth blueprint from the 'api' folder
from flask_app.models import db  # Import the database instance
from flask_app.api.market import market_bp  # Import the market blueprint
from flask_app.api.trade import trade_bp  # Import the trade blueprint

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# PostgreSQL Database URI and configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security Configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    REMEMBER_COOKIE_SECURE=True,
    REMEMBER_COOKIE_HTTPONLY=True
)

# Register blueprints with unique prefixes
app.register_blueprint(auth_bp, url_prefix='/api/auth')  # Auth Blueprint with /api/auth prefix
app.register_blueprint(market_bp, url_prefix='/api/market')  # Market Blueprint with /api/market prefix
app.register_blueprint(trade_bp, url_prefix='/api/trade')  # Trade Blueprint with /api/trade prefix

# Initialize the database with the Flask app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Home route to test database connectivity
@app.route('/')
def home():
    try:
        result = db.session.execute("SELECT 1")
        return f"Database is connected! Query result: {result.fetchone()[0]}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
