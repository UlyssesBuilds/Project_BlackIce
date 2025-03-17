# models.py
from datetime import datetime
from decimal import Decimal
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  # MUST BE PLURAL
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(60), nullable=False)  # BCrypt only
    balance = db.Column(db.Numeric(10, 2), default=Decimal('0.00'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Market(db.Model):
    __tablename__ = 'markets'  # PLURAL
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="open", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bet(db.Model):
    __tablename__ = 'bets'  # PLURAL
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # Plural reference
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False, index=True)  # Plural
    bet_amount = db.Column(db.Numeric(10, 2), nullable=False)
    outcome = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'  # PLURAL
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # Plural
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))