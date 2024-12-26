from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Transaction, User
from datetime import datetime, timedelta
import numpy as np

from app.services.check_alerts_and_notify import check_alerts_and_notify

transactions_bp = Blueprint('transactions', __name__)


# API Endpoints
@transactions_bp.route('', methods=['POST'])
@jwt_required()
def add_transaction():
    data = request.get_json()

    # Validate input
    if not data:
        return jsonify({"msg": "No data provided."}), 400

    user_id = get_jwt_identity()

    if int(user_id) != data.get('user_id'):
        return jsonify({"msg": "No empty fields allowed."}), 403

    amount = data.get('amount')
    category = data.get('category')
    timestamp = data.get('timestamp')

    if not all([amount, category]):
        return jsonify({"msg": "No empty fields allowed."}), 400

    fraud = False
    user = User.query.get(user_id)

    try:
        if category in ['deposit ATM', 'deposit', 'received_transfer', 'bizum']:
            user.balance += amount
            check_alerts_and_notify(user, amount, True)
        else:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ') if timestamp else datetime.now()
            avg, std_dev = calculate_average_and_std(user_id)
            categories = recent_categories(user_id)
            transactions = rapid_transactions(user_id, timestamp)

            # Fraud detection
            if amount > avg + (3 * std_dev) and avg != 0:
                fraud = True
            elif categories and category not in categories:
                fraud = True
            elif len(transactions) > 3 and sum(txn.amount for txn in transactions) > avg:
                fraud = True

            user.balance -= amount

        # Save transaction
        new_transaction = Transaction(
            user_id=user_id,
            amount=amount,
            category=category,
            timestamp=timestamp,
            fraud=fraud
        )
        db.session.add(new_transaction)
        db.session.commit()

        if fraud:
            check_alerts_and_notify(user, amount, False)

        return jsonify({"msg": "Transaction added and evaluated for fraud.", "data": {
            "id": new_transaction.id,
            "user_id": new_transaction.user_id,
            "amount": new_transaction.amount,
            "category": new_transaction.category,
            "timestamp": new_transaction.timestamp.isoformat(),
            "fraud": new_transaction.fraud
        }}), 201

    except Exception as e:
        return jsonify({"msg": "Error occurred while adding transaction."}), 400


# Helper Functions
def calculate_average_and_std(user_id, days=90):
    cutoff_date = datetime.now() - timedelta(days=days)
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.timestamp >= cutoff_date
    ).all()
    amounts = [txn.amount for txn in transactions]
    if amounts:
        avg = np.mean(amounts)
        std_dev = np.std(amounts)
    else:
        avg, std_dev = 0, 0
    return avg, std_dev


def recent_categories(user_id, months=6):
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.timestamp >= cutoff_date
    ).all()
    return set(txn.category for txn in transactions)


def rapid_transactions(user_id, current_time, threshold=5, max_count=3):
    cutoff_time = current_time - timedelta(minutes=threshold)
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.timestamp >= cutoff_time
    ).all()
    return transactions