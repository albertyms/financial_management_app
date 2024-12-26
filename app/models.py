from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_amount = db.Column(db.Float, nullable=True, default=0.0)
    alert_threshold = db.Column(db.Float, nullable=True, default=0.0)
    balance_drop_threshold = db.Column(db.Float, nullable=True, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

class RecurringExpense(db.Model):
    __tablename__ = 'recurring_expenses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expense_name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)
    fraud = db.Column(db.Boolean, default=False, nullable=False)
