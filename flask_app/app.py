from flask import Flask
from dotenv import load_dotenv
import os
from flask_migrate import Migrate  # Import Migrate
from sqlalchemy import text  # Import text function

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# PostgreSQL Database URI from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import the db instance from models.py
from models import db, User, Market, Bet, Transaction  # Ensure models are imported

# Initialize the db with the Flask app
db.init_app(app)

# Initialize Flask-Migrate with the app and the single db instance
migrate = Migrate(app, db)

@app.route('/')
def home():
    try:
        # Use the text() function to wrap the query
        result = db.session.execute(text('SELECT 1'))
        return f"Database is connected! Query result: {result.fetchone()[0]}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)