import time
from pyseto import Key, Paseto
from pyseto.exceptions import PysetoError

SECRET_KEY = 'your_secret_key'  # Replace with your actual secret key

def generate_paseto_token(email, account_type):
    expiration = int(time.time()) + 300
    payload = {
        'email': email,
        'account_type': account_type,
        'exp': expiration
    }
    # Create a key for version 4, local (symmetric) encryption
    key = Key.new(4, purpose="local", key=SECRET_KEY.encode())
    token = Paseto.encode(key, payload)
    return token

def verify_paseto_token(token, email, account_type):
    try:
        # Create a key for version 4, local (symmetric) encryption
        key = Key.new(4, purpose="local", key=SECRET_KEY.encode())
        payload = Paseto.decode(key, token)
        if payload['email'] == email and payload['account_type'] == account_type:
            return True
        else:
            return False
    except PysetoError:
        return False