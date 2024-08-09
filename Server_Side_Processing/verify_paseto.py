from datetime import datetime, timedelta
import paseto
from flask import current_app
from ..app_routes.email_util import send_email

# Constants
TOKEN_EXPIRY_MINUTES = 5

# Generate a PASETO token
def generate_paseto_token(email, account_type):
    payload = {
        "email": email,
        "account_type": account_type,
        "exp": (datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)).timestamp()
    }
    token = paseto.create(
        purpose='local',
        payload=payload,
        key=current_app.config['SECRET_KEY']
    )
    return token

# Verify the PASETO token
def verify_paseto_token(token):
    try:
        payload = paseto.parse(
            purpose='local',
            token=token,
            key=current_app.config['SECRET_KEY']
        )
        if datetime.utcnow().timestamp() > payload['exp']:
            return None  # Token expired
        return payload
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

# Send verification email
def send_verification_email(email, account_type, token):
    subject = "Account Verification"
    verification_link = f"{current_app.config['BASE_URL']}/verify/{token}"
    message = f"Please verify your account by clicking on the following link: {verification_link}"
    send_email(subject, message, email)

# Send confirmation email after successful verification
def send_confirmation_email(email):
    subject = "Account Verified"
    message = "Your account has been successfully verified."
    send_email(subject, message, email)

# Resend verification email
def resend_verification_email(email, account_type):
    token = generate_paseto_token(email, account_type)
    send_verification_email(email, account_type, token)
