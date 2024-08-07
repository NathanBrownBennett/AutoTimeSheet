# Server_Side_Processing/verify_paseto.py
import paseto
from datetime import datetime, timedelta

SECRET_KEY = b'your-256-bit-secret'  # Replace with your actual secret key

def generate_paseto_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": (datetime.utcnow() + timedelta(hours=1)).isoformat()  # Token expiration time
    }
    token = paseto.create(key=SECRET_KEY, purpose='local', claims=payload)
    return token

def verify_paseto_token(token):
    try:
        payload = paseto.parse(key=SECRET_KEY, purpose='local', token=token)
        return payload['user_id']
    except paseto.PasetoException:
        return None