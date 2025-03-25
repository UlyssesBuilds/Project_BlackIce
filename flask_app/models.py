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
    __tablename__ = 'markets' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    outcome_yes_price = db.Column(db.Float, default=0.5)  # 50-50 split at start
    outcome_no_price = db.Column(db.Float, default=0.5)
    is_resolved = db.Column(db.Boolean, default=False)
    final_outcome = db.Column(db.String(10), nullable=True)  # "yes" or "no"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "outcome_yes_price": self.outcome_yes_price,
            "outcome_no_price": self.outcome_no_price,
            "is_resolved": self.is_resolved,
            "final_outcome": self.final_outcome
        }


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

class Trade(db.Model):
    __tablename__ = 'trades' 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('market.id'), nullable=False)
    outcome = db.Column(db.String(10), nullable=False)  # "yes" or "no"
    amount = db.Column(db.Float, nullable=False)  # How much they bet
    price = db.Column(db.Float, nullable=False)  # At what price they bought

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "market_id": self.market_id,
            "outcome": self.outcome,
            "amount": self.amount,
            "price": self.price
        }