from app.models import User, Alert
from app.utils.email_service import send_email


def check_alerts_and_notify(user, transaction_amount, increase_or_drop_threshold):
    """
    Check for triggered alerts and send email notifications to the user.
    This service handles all checks for alerts and sends emails as necessary.
    """
    # Fetch user details
    if not user:
        return {"msg": "User not found."}, 404

    # Retrieve all alerts for the user
    alerts = Alert.query.filter_by(user_id=user.id).all()
    if not alerts:
        return {"msg": "No alerts found for user."}, 404

    for alert in alerts:
        # Trigger a savings goal email if the target amount is met or exceeded
        if increase_or_drop_threshold:
            if alert.target_amount and user.balance >= alert.target_amount:
                email_body = f"""
                    Dear {user.name},
    
                    Great news! Your savings are nearing the target amount of {alert.target_amount}.
                    Keep up the great work and stay consistent!
    
                    Best Regards,
                    The Management Team
                    """
                try:
                    send_email(
                        subject="Savings Alert!",
                        recipients=[user.email],
                        body=email_body
                    )
                except:
                    ...
        else:
            # Trigger a balance drop email if the transaction drops the balance significantly
            if alert.balance_drop_threshold and transaction_amount <= alert.balance_drop_threshold:
                email_body = f"""
                    Dear {user.name},
    
                    We noticed a significant balance drop in your account more than {alert.balance_drop_threshold}.
                    If this wasn't you, please review your recent transactions to ensure everything is correct.
    
                    Best Regards,
                    The Management Team
                    """
                try:
                    send_email(
                        subject="Balance Drop Alert!",
                        recipients=[user.email],
                        body=email_body
                    )
                except:
                    ...
