import time
from paseto import PasetoV2
#from paseto.v2 import PasetoV2Public as PasetoV2
from paseto.exceptions import PasetoException
from ..app_routes.email_util import resend_verification_email

SECRET_KEY = 'your_secret_key'  # Replace with your actual secret key

def generate_paseto_token(email, account_type):
    expiration = int(time.time()) + 300
    payload = {
        'email': email,
        'account_type': account_type,
        'exp': expiration
    }
    return PasetoV2.sign(payload, SECRET_KEY)

def verify_paseto_token(token, email, account_type):
    try:
        payload = PasetoV2.verify(token, SECRET_KEY)
        if payload['email'] == email and payload['account_type'] == account_type:
            return True
        else:
            return False
    except PasetoException:
        return False