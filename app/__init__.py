# app/__init__.py
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.routes.recurring_expenses import recurring_expenses_bp
    app.register_blueprint(recurring_expenses_bp, url_prefix='/api/recurring-expenses')

    from app.routes.transfers import transfers_bp
    app.register_blueprint(transfers_bp, url_prefix='/api/transfers')

    from app.routes.alerts import alerts_bp
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')

    from app.routes.transactions import transactions_bp
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')

    # Create tables automatically
    with app.app_context():
        db.create_all()

    return app