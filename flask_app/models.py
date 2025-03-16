from flask_sqlalchemy import SQLAlchemy
import hashlib
import os
import uuid
from datetime import datetime
from decimal import Decimal

# Define a single instance of SQLAlchemy here
db = SQLAlchemy()

# Secure hashing function for passwords & sensitive data
def hash_data(data: str, salt: str = None):
    if not salt:
        salt = os.urandom(16).hex()  # Generate a new salt if not provided
    hash_object = hashlib.sha256((salt + data).encode())
    return f"{salt}${hash_object.hexdigest()}"  # Store salt and hash together

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=Decimal('0.00'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = hash_data(password)

    def check_password(self, password):
        salt, stored_hash = self.password_hash.split('$')
        return hash_data(password, salt).split('$')[1] == stored_hash

class Market(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="open", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False, index=True)
    market_id = db.Column(db.Integer, db.ForeignKey('market.id', ondelete="CASCADE"), nullable=False, index=True)
    bet_amount = db.Column(db.Numeric(10, 2), nullable=False)
    outcome = db.Column(db.String(10), nullable=False)  # 'Yes' or 'No'
    status = db.Column(db.String(10), default="pending")  # 'pending', 'won', 'lost'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(15), nullable=False)  # 'deposit', 'withdrawal', 'bet', 'payout'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    @staticmethod
    def log_transaction(user_id, amount, transaction_type):
        """Logs transactions into the database instead of a flat file."""
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            transaction_id=str(uuid.uuid4())
        )
        db.session.add(transaction)
        db.session.commit()