from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from jwt.exceptions import InvalidSubjectError

from app import db
from app.models import RecurringExpense
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

recurring_expenses_bp = Blueprint('recurring_expenses', __name__)


@jwt_required()
@recurring_expenses_bp.route('', methods=['GET'])
def get_recurring_expenses():
    try:
        verify_jwt_in_request()
    except InvalidSubjectError as e:
        return jsonify({"msg": "Invalid token"}), 400

    user_id = get_jwt_identity()
    expenses = RecurringExpense.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": expense.id,
        "expense_name": expense.expense_name,
        "amount": expense.amount,
        "frequency": expense.frequency,
        "start_date": expense.start_date.strftime("%Y-%m-%d")
    } for expense in expenses]), 200


@jwt_required()
@recurring_expenses_bp.route('', methods=['POST'])
def add_recurring_expense():
    data = request.get_json()

    # Validate input
    if not data:
        return jsonify({"msg": "No data provided."}), 400

    expense_name = data.get('expense_name')
    amount = data.get('amount')
    frequency = data.get('frequency')
    start_date = data.get('start_date')

    if not all([expense_name, amount, frequency, start_date]):
        return jsonify({"msg": "No empty fields allowed."}), 400

    try:
        verify_jwt_in_request()
    except InvalidSubjectError as e:
        return jsonify({"msg": "Invalid token"}), 400

    # Get user
    user_id = int(get_jwt_identity())

    try:
        new_expense = RecurringExpense(
            user_id=user_id,
            expense_name=expense_name,
            amount=amount,
            frequency=frequency,
            start_date=datetime.strptime(start_date, '%Y-%m-%d')
        )
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({"msg": "Recurring expense added successfully.", "data": {
            "id": new_expense.id,
            "expense_name": new_expense.expense_name,
            "amount": new_expense.amount,
            "frequency": new_expense.frequency,
            "start_date": new_expense.start_date.strftime('%Y-%m-%d')
        }}), 201

    except Exception as e:
        return jsonify({"msg": "Error occurred while adding expense."}), 400


@jwt_required()
@recurring_expenses_bp.route('/<int:expense_id>', methods=['PUT'])
def update_recurring_expense(expense_id):

    try:
        verify_jwt_in_request()
    except InvalidSubjectError as e:
        return jsonify({"msg": "Invalid token"}), 400

    user_id = get_jwt_identity()
    expense = RecurringExpense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"msg": "Expense not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "No data provided."}), 400

    expense_name = data.get('expense_name')
    amount = data.get('amount')
    frequency = data.get('frequency')
    start_date = data.get('start_date')

    if not all([expense_name, amount, frequency, start_date]):
        return jsonify({"msg": "No empty fields allowed."}), 400

    try:
        expense.expense_name = expense_name
        expense.amount = amount
        expense.frequency = frequency
        expense.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        db.session.commit()
        return jsonify({
            "msg": "Recurring expense updated successfully.",
            "data": {
                "id": expense.id,
                "expense_name": expense.expense_name,
                "amount": expense.amount,
                "frequency": expense.frequency,
                "start_date": expense.start_date
            }
        }), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"msg": "Database error during update."}), 400


@recurring_expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_recurring_expense(expense_id):

    try:
        verify_jwt_in_request()
    except InvalidSubjectError as e:
        return jsonify({"msg": "Invalid token"}), 400

    user_id = get_jwt_identity()
    expense = RecurringExpense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"msg": "Expense not found."}), 404

    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({"msg": "Recurring expense deleted successfully."}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"msg": "Database error during deletion."}), 400


@recurring_expenses_bp.route('/projection', methods=['GET'])
@jwt_required()
def get_projection():
    user_id = get_jwt_identity()
    expenses = RecurringExpense.query.filter_by(user_id=user_id).all()

    projection = []
    current_date = datetime.now()

    # Loop through the next 12 months
    for month_offset in range(12):
        # Calculate the start of the month
        month_start_year = current_date.year + (current_date.month + month_offset - 1) // 12
        month_start_month = (current_date.month + month_offset - 1) % 12 + 1
        month_start = datetime(month_start_year, month_start_month, 1)

        # Sum up expenses for the month
        month_expenses = 0.0
        for expense in expenses:
            if expense.start_date <= month_start and expense.frequency == 'monthly':
                month_expenses += expense.amount

        projection.append({
            "month": month_start.strftime('%Y-%m'),
            "recurring_expenses": round(month_expenses, 2)
        })

    return jsonify(projection), 200