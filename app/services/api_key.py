import secrets
import string

def generate_api_key():
    key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    return key
