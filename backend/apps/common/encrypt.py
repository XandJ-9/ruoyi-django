import base64
import hashlib
from django.conf import settings

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:
    Fernet = None
    InvalidToken = Exception


def _get_fernet():
    if Fernet is None:
        raise RuntimeError('cryptography not installed')
    secret = settings.SECRET_KEY
    digest = hashlib.sha256(secret.encode('utf-8')).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_password(password):
    if password is None:
        return ''
    f = _get_fernet()
    token = f.encrypt(str(password).encode('utf-8'))
    return 'enc:' + token.decode('utf-8')


def decrypt_password(password):
    if not password:
        return ''
    s = str(password)
    if not s.startswith('enc:'):
        return s
    f = _get_fernet()
    token = s[4:].encode('utf-8')
    try:
        return f.decrypt(token).decode('utf-8')
    except InvalidToken:
        return ''
