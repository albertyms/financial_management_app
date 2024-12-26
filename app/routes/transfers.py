import csv
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

transfers_bp = Blueprint('transfers', __name__)


@jwt_required()
@transfers_bp.route('/simulate', methods=['POST'])
def simulate_transfer():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided."}), 400

    amount = data.get('amount')
    source_currency = data.get('source_currency')
    target_currency = data.get('target_currency')

    if not all([amount, source_currency, target_currency]):
        return jsonify({"msg": "No empty fields allowed."}), 400

    # Retrieve rate and fee
    rate_key = (source_currency, target_currency)
    fee_key = (source_currency, target_currency)
    rate = exchange_rates.get(rate_key)
    fee = exchange_fees.get(fee_key)

    if rate is None or fee is None:
        return jsonify({"msg": "Invalid currencies or no exchange data available."}), 404

    # Calculate target amount
    net_amount = amount * (1 - fee)
    target_amount = net_amount * rate

    return jsonify({"msg": f"Amount in target currency: {round(target_amount, 2)}."}), 201


@jwt_required()
@transfers_bp.route('/fees', methods=['GET'])
def get_transfer_fees():
    source_currency = request.args.get('source_currency')
    target_currency = request.args.get('target_currency')

    if not all([source_currency, target_currency]):
        return jsonify({"msg": "No empty fields allowed."}), 400

    fee = exchange_fees.get((source_currency, target_currency))
    if fee is None:
        return jsonify({"msg": "No fee information available for these currencies."}), 404

    return jsonify({"fee": fee}), 200


@jwt_required()
@transfers_bp.route('/rates', methods=['GET'])
def get_exchange_rate():
    source_currency = request.args.get('source_currency')
    target_currency = request.args.get('target_currency')

    if not all([source_currency, target_currency]):
        return jsonify({"msg": "No empty fields allowed."}), 400

    rate = exchange_rates.get((source_currency, target_currency))
    if rate is None:
        return jsonify({"msg": "No exchange rate available for these currencies."}), 404

    return jsonify({"rate": rate}), 200


# Load exchange rates from CSV
def load_exchange_rates():
    rates = {}
    with open('app/exchange_rates.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rates[(row['source_currency'], row['target_currency'])] = float(row['rate'])
    return rates

# Load exchange fees from CSV
def load_exchange_fees():
    fees = {}
    with open('app/exchange_fees.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            fees[(row['source_currency'], row['target_currency'])] = float(row['fee'])
    return fees

exchange_rates = load_exchange_rates()
exchange_fees = load_exchange_fees()
