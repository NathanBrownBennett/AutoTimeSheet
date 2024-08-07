# Server_Side_Processing/verify_paseto.py for handling app logins and user verification
import paseto
from datetime import datetime, timedelta

def get_secret_key(organization_name, user_id):
    user_name_length = len(user_id)
    secret_key = f'{organization_name}-{user_name_length}-secret-key'.encode('utf-8')
    return secret_key

SECRET_KEY = get_secret_key(organization_name, user_id)

def verify_account_type(email, password):
    email_domain = email.split('@')[1]
    email_classes = ['superadmin', 'organisation', 'employee']
    if email_domain == 'superadmin':
        return True
        

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