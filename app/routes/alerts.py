from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Alert
from datetime import datetime

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/amount_reached', methods=['POST'])
@jwt_required()
def add_amount_reached_alert():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided."}), 400

    target_amount = data.get('target_amount')
    alert_threshold = data.get('alert_threshold')

    if not all([target_amount, alert_threshold]):
        return jsonify({"msg": "No empty fields allowed."}), 400

    user_id = get_jwt_identity()

    try:
        new_alert = Alert(
            user_id=user_id,
            target_amount=target_amount,
            alert_threshold=alert_threshold,
            balance_drop_threshold=None  # Not applicable for this type of alert
        )
        db.session.add(new_alert)
        db.session.commit()

        return jsonify({"msg": "Correctly added savings alert!", "data": {
            "id": new_alert.id,
            "user_id": new_alert.user_id,
            "target_amount": new_alert.target_amount,
            "alert_threshold": new_alert.alert_threshold
        }}), 201

    except Exception as e:
        return jsonify({"msg": "Error occurred while creating alert."}), 400


@alerts_bp.route('/balance_drop', methods=['POST'])
@jwt_required()
def add_balance_drop_alert():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided."}), 400

    balance_drop_threshold = data.get('balance_drop_threshold')

    if not balance_drop_threshold:
        return jsonify({"msg": "No empty fields allowed."}), 400

    user_id = get_jwt_identity()

    try:
        new_alert = Alert(
            user_id=user_id,
            target_amount=None,  # Not applicable for this type of alert
            alert_threshold=None,
            balance_drop_threshold=balance_drop_threshold
        )
        db.session.add(new_alert)
        db.session.commit()

        return jsonify({"msg": "Correctly added balance drop alert!", "data": {
            "id": new_alert.id,
            "user_id": new_alert.user_id,
            "balance_drop_threshold": new_alert.balance_drop_threshold
        }}), 201

    except Exception as e:
        return jsonify({"msg": "Error occurred while creating alert."}), 400


@alerts_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_alert():
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided."}), 400

    if not data.get('alert_id'):
        return jsonify({"msg": "No empty fields allowed."}), 400

    alert_id = data.get('alert_id')

    if not alert_id:
        return jsonify({"msg": "Missing alert ID."}), 400

    user_id = get_jwt_identity()
    alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()

    if not alert:
        return jsonify({"msg": "Alert not found."}), 404

    try:
        db.session.delete(alert)
        db.session.commit()

        return jsonify({"msg": "Alert deleted successfully."}), 200

    except Exception as e:
        return jsonify({"msg": "Error occurred while deleting alert."}), 400


@alerts_bp.route('/list', methods=['GET'])
@jwt_required()
def list_alerts():
    user_id = get_jwt_identity()
    alerts = Alert.query.filter_by(user_id=user_id).all()

    return jsonify({"data": [{
        "id": alert.id,
        "user_id": alert.user_id,
        "target_amount": alert.target_amount,
        "alert_threshold": alert.alert_threshold,
        "balance_drop_threshold": alert.balance_drop_threshold,
    } for alert in alerts]}), 200
