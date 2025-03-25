# flask_app/api/auth.py
import os
import re
import bcrypt
import jwt
import datetime
from datetime import timedelta
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_app.models import db, User

# Initialize the blueprint and limiter
auth_bp = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address)

# --- Constants for validation (optional) ---
MIN_PASSWORD_LENGTH = 12
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validate_input(email: str, password: str) -> tuple:
    """Returns (is_valid, error_message) tuple."""
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format"
    if not PASSWORD_REGEX.match(password):
        return False, ("Password must contain: 12+ chars, uppercase, lowercase, number, special char")
    return True, ""

# --- Routes ---

# Registration Form (GET) - for full-stack, you might render a template instead.
@auth_bp.route('/register', methods=['GET'])
def register_page():
    return '''
    <form action="/api/auth/register" method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Register</button>
    </form>
    '''

# Registration Processing (POST)
@auth_bp.route('/register', methods=['POST'])
def register_user():
    try:
        # Handle JSON vs form explicitly (REMOVED THE REDUNDANT LINE)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not all([email, username, password]):
            return jsonify({"message": "Missing required fields"}), 400

        is_valid, msg = validate_input(email, password)
        if not is_valid:
            return jsonify({"message": msg}), 400

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({"message": "Username or email already exists"}), 409

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
        new_user = User(username=username, email=email, password_hash=hashed_pw.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"message": "Registration failed"}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"message": "Registration failed"}), 500

# Login Form (GET)
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return '''
    <form action="/api/auth/login" method="POST">
        <input type="text" name="username_or_email" placeholder="Username or Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    '''

# Login Processing (POST)
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute", override_defaults=False)
def login_user():
    try:
        # Explicit content type check (REMOVED THE REDUNDANT LINE)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')

        if not all([username_or_email, password]):
            return jsonify({"message": "Missing credentials"}), 400

        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({"message": "Invalid credentials"}), 401

        secret = os.environ.get('JWT_SECRET_KEY')
        if not secret:
            raise ValueError("Missing JWT secret in environment")

        token = jwt.encode({
            'sub': user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
            'iss': 'your-app-name',
            'aud': 'your-app-client'
        }, secret, algorithm='HS256')

	# Return token only for successful login
        return jsonify({"token": token, "expires_in": 3600}), 200
        

	# we need to come back and edit this for HTTPSonly but am passing back JSON token for now
        #response = jsonify({"token": token, "expires_in": 3600})
        #response.set_cookie('auth_token', value=token, httponly=True, secure=True, samesite='Strict', max_age=3600)



    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"message": "Login failed"}), 500