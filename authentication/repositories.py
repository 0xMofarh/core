from .models import CustomUser, OTP,PasswordResetCode
from django.utils import timezone
from django.utils.crypto import get_random_string


class UserRepository:
    def create_user(self, email, password, full_name, mobile_number):
        return CustomUser.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            mobile_number=mobile_number,
            is_active=True,
            is_email_verified=False
        )
    
    def email_exists(self, email):
        return CustomUser.objects.filter(email=email).exists()
    
    def update_last_login(self, user):
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

    def get_user_by_email(self, email):
        return CustomUser.objects.filter(email=email).first()

    def save(self, user):
        user.save()
        return user


class OTPRepository:
    def create_otp(self, user, purpose, code=None):
        if code is None:
            code = OTP.generate_code()
        return OTP.create_otp(user, purpose)

    def get_valid_otp(self, user, code):
        """إرجاع OTP صالح وغير منتهي وغير مفعل"""
        return OTP.objects.filter(
            user=user,
            code=code,
            is_verified=False,
            expires_at__gt=timezone.now()
        ).first()

    def mark_as_verified(self, otp):
        otp.is_verified = True
        otp.save(update_fields=['is_verified'])

class PasswordResetRepository:
    def create_reset_code(self, user):
        # إنشاء كود 6 أرقام عشوائي
        code = get_random_string(length=6, allowed_chars='0123456789')
        reset_obj = PasswordResetCode.objects.create(user=user, code=code)
        return reset_obj

    def verify_code(self, user, code):
        obj = PasswordResetCode.objects.filter(user=user, code=code, used=False).first()
        if obj:
            obj.used = True
            obj.save(update_fields=['used'])
            return True
        return False