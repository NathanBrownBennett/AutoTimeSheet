from datetime import datetime, timedelta
import paseto
from flask import current_app

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