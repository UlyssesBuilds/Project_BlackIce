from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from sqlalchemy import text  # Import text function

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# PostgreSQL Database URI from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define your routes
@app.route('/')
def home():
    try:
        # Use the text() function to wrap the query
        result = db.session.execute(text('SELECT 1'))
        return f"Database is connected! Query result: {result.fetchone()[0]}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)