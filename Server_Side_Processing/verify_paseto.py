import random
#import os
import math
import time
from ..models import User, Organisation
from datetime import datetime

ACCOUNT_TYPE_MAP = {
    'organisation': Organisation,
    'employee': User,
    'guest': User
}

def verify_code(email, verification_code, account_type):
    model = ACCOUNT_TYPE_MAP.get(account_type)
    if not model:
        return False
    account = model.query.filter_by(email=email).first()
    if not account:
        return False
    code = account.last_generated_code
    expiry = account.last_generated_code_time
    expired_status = check_expired(expiry)
    if verification_code == code and not expired_status:
        return True
    else:
        return False

def generate_code(email, account_type):
    model = ACCOUNT_TYPE_MAP.get(account_type)
    if not model:
        return None
    code = math.floor(random.random() * 9000000) + 1000000
    account = model.query.filter_by(email=email).first()
    if not account:
        return None
    account.last_generated_code = code
    account.last_generated_code_time = datetime.fromtimestamp(time.time())
    return code

def check_expired(expiry):
    current_time = time.time()
    expired = False
    if current_time - expiry > 600:
        expired = True
    return expired