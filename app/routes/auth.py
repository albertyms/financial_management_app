from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate data
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if email is None or password is None or name is None:
        return jsonify({"error": "All fields are required."}), 400
    if email is "" or password is "" or name is "":
        return jsonify({"error": "No empty fields allowed."}), 400
    if not isinstance(email, str) or "@" not in email:
        return jsonify({"error": "Invalid email."}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists."}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create user
    new_user = User(email=email, hashed_password=hashed_password, name=name)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "name": new_user.name,
        "email": new_user.email,
        "hashedPassword": hashed_password
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate data
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Bad credentials."}), 401

    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": f"User not found for the given email: {email}"}), 400

    # Check password
    if not bcrypt.check_password_hash(user.hashed_password, password):
        return jsonify({"error": "Bad credentials."}), 401

    # Generate JWT token
    token = create_access_token(identity=str(user.id))

    return jsonify({"token": token}), 200
