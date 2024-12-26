class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:123456789@db/financial_management'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'

    # Flask-Mail Configuration
    MAIL_SERVER = "smtp.gmail.com"  # e.g., Gmail's SMTP server
    MAIL_PORT = 587  # Port for the mail server
    MAIL_USE_TLS = True  # Use TLS for secure connection
    MAIL_USERNAME = "your_email@gmail.com"  # SMTP username
    MAIL_PASSWORD = "your_password"  # SMTP password
    MAIL_DEFAULT_SENDER = "no-reply@yourapp.com"