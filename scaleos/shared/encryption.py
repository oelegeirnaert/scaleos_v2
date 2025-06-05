from cryptography.fernet import Fernet
from django.conf import settings


class KeyManager:
    @staticmethod
    def get_fernet():
        key = getattr(settings, "ENCRYPTION_KEY", None)
        if not key:
            msg = "Missing ENCRYPTION_KEY in Django settings."
            raise ValueError(msg)
        return Fernet(key)
