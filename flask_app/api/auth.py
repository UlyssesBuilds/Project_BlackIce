import os
import re
import bcrypt
import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)  # Will init with app later

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

# --- Constants ---
MIN_PASSWORD_LENGTH = 12
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# --- Models ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(60), nullable=False)  # BCrypt fixed length

# --- Helper Functions ---
def validate_input(email: str, password: str) -> tuple:
    """Returns (is_valid, error_message) tuple"""
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format"
    if not PASSWORD_REGEX.match(password):
        return False, ("Password must contain: "
                       "12+ chars, uppercase, lowercase, number, special char")
    return True, ""

# --- Routes ---
@auth_bp.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        # Validate input
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not all([email, username, password]):
            return jsonify({"message": "Missing required fields"}), 400

        is_valid, msg = validate_input(email, password)
        if not is_valid:
            return jsonify({"message": msg}), 400

        # Check existing users
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({"message": "Username or email already exists"}), 409

        # Hash password with bcrypt
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

        # Create user
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

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute", override_defaults=False)
def login_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        # Get credentials
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')

        if not all([username_or_email, password]):
            return jsonify({"message": "Missing credentials"}), 400

        # Find user
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({"message": "Invalid credentials"}), 401

        # Generate JWT
        secret = os.environ.get('JWT_SECRET_KEY')
        if not secret:
            raise ValueError("Missing JWT secret in environment")

        token = jwt.encode({
            'sub': user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
            'iss': 'your-app-name',
            'aud': 'your-app-client'
        }, secret, algorithm='HS256')

        response = jsonify({
            "message": "Login successful",
            "token": token,
            "expires_in": 3600
        })
        
        # Set secure cookie (alternative to returning in body)
        response.set_cookie(
            'auth_token',
            value=token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=3600
        )
        
        return response

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"message": "Login failed"}), 500

# --- Security Configuration (Add to app.py) ---
# In your app initialization:
# app.config.update(
#     SESSION_COOKIE_SECURE=True,
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE='Strict',
#     REMEMBER_COOKIE_SECURE=True,
#     REMEMBER_COOKIE_HTTPONLY=True
# )