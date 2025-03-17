from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from flask_migrate import Migrate  # Import Migrate
from sqlalchemy import text  # Import text function
from flask_app.api.auth import auth_bp  # Import the 'auth' blueprint

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Register the auth blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')  # Prefix is optional

# Get the JWT secret key
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

# PostgreSQL Database URI from environment variables
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

# Import the db instance from models.py
from flask_app.models import db, User, Market, Bet, Transaction  # Ensure models are imported


from flask_app.api.auth import register_user, login_user  # Make sure to import from 'api.auth'


# Initialize the db with the Flask app
db.init_app(app)

# Initialize Flask-Migrate with the app and the single db instance
migrate = Migrate(app, db)

#MVP of database querying working (postgreSQL)
@app.route('/')
def home():
    try:
        # Use the text() function to wrap the query
        result = db.session.execute(text('SELECT 1'))
        return f"Database is connected! Query result: {result.fetchone()[0]}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

#MVP with quick HTML embedded to check login and registration API
@app.route('/login', methods=['GET'])
def login_page():
    return '''
        <form action="/login" method="POST">
            <label for="username_or_email">Username or Email:</label>
            <input type="text" id="username_or_email" name="username_or_email" required>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/login', methods=['POST'])
def login_user():
    data = {
        'username_or_email': request.form['username_or_email'],
        'password': request.form['password']
    }
    
    # Check if the user exists by username or email
    user = User.query.filter((User.username == data['username_or_email']) | (User.email == data['username_or_email'])).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Check if the password is correct
    if not user.check_password(data['password']):
        return jsonify({"message": "Incorrect password"}), 401
    
    # Generate a JWT token with an expiration time (e.g., 1 hour)
    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
        os.getenv('JWT_SECRET_KEY'),  # Use the secret key from .env file
        algorithm='HS256'
    )
    
    return jsonify({"message": "Login successful", "token": token}), 200


if __name__ == '__main__':
    app.run(debug=True)