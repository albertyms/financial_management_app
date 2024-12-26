from flask_mail import Message
from app import mail


def send_email(subject, recipients, body):
    """
    Send an email using Flask-Mail.
    """
    try:
        msg = Message(subject, recipients=recipients, body=body)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
