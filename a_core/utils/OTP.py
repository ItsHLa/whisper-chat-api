import pyotp
from django.core.cache import cache

class OTP:
    
    @staticmethod
    def generate(value):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=300)
        otp = totp.now()
        cache.set(f'otp_{value}', secret, timeout=300)
        return otp
    
    @staticmethod
    def verify(value, otp):
        secret = cache.get(f'otp_{value}')
        if not secret:
            return False
        totp = pyotp.TOTP(secret, interval=300)
        return totp.verify(otp)